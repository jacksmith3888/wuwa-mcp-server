"""Enhanced HTTP client with retry logic and circuit breaker pattern."""

import asyncio
import json
from types import TracebackType
from typing import Any

import httpx

from ...core.config import APISettings
from ...core.config import HTTPClientSettings
from ...core.exceptions import APIException
from ...core.exceptions import AuthenticationException
from ...core.exceptions import ConnectionException
from ...core.exceptions import RateLimitException
from ...core.logging_config import LoggerMixin


class CircuitBreaker:
    """Simple circuit breaker implementation."""

    def __init__(self, failure_threshold: int = 5, timeout: float = 60.0):
        """Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before opening circuit.
            timeout: Seconds to wait before trying again after circuit opens.
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time: float | None = None
        self.state = "closed"  # closed, open, half-open

    def can_execute(self) -> bool:
        """Check if request can be executed."""
        current_time = asyncio.get_event_loop().time()

        if self.state == "closed":
            return True
        elif self.state == "open":
            if self.last_failure_time and (current_time - self.last_failure_time) > self.timeout:
                self.state = "half-open"
                return True
            return False
        else:  # half-open
            return True

    def record_success(self) -> None:
        """Record successful execution."""
        self.failure_count = 0
        self.state = "closed"

    def record_failure(self) -> None:
        """Record failed execution."""
        self.failure_count += 1
        self.last_failure_time = asyncio.get_event_loop().time()

        if self.failure_count >= self.failure_threshold:
            self.state = "open"


class HTTPClient(LoggerMixin):
    """Enhanced HTTP client with retry logic, circuit breaker, and better error handling."""

    def __init__(
        self,
        api_settings: APISettings,
        http_settings: HTTPClientSettings,
        enable_circuit_breaker: bool = True,
    ):
        """Initialize HTTP client.

        Args:
            api_settings: API configuration settings.
            http_settings: HTTP client configuration settings.
            enable_circuit_breaker: Whether to enable circuit breaker.
        """
        self.api_settings = api_settings
        self.http_settings = http_settings
        self._client: httpx.AsyncClient | None = None

        # Circuit breaker
        self.circuit_breaker = CircuitBreaker() if enable_circuit_breaker else None

        # Build headers
        self._headers = self._build_headers()

    def _build_headers(self) -> dict[str, str]:
        """Build HTTP headers from settings."""
        return {
            "User-Agent": self.http_settings.user_agent,
            "Origin": self.http_settings.origin,
            "Referer": self.http_settings.referer,
            "Source": self.http_settings.source,
            "Content-Type": self.http_settings.content_type,
            "Accept": self.http_settings.accept,
            "Accept-Encoding": self.http_settings.accept_encoding,
            "wiki_type": self.http_settings.wiki_type,
        }

    async def __aenter__(self) -> "HTTPClient":
        """Async context manager entry."""
        self._client = httpx.AsyncClient(
            headers=self._headers,
            timeout=httpx.Timeout(self.api_settings.timeout),
            limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
        )
        self.logger.info("HTTP client initialized")
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None = None,
        exc_value: BaseException | None = None,
        traceback: TracebackType | None = None,
    ) -> None:
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()
            self._client = None
            self.logger.info("HTTP client closed")

    async def post_with_retry(
        self,
        endpoint: str,
        data: dict[str, Any],
        max_retries: int | None = None,
    ) -> dict[str, Any]:
        """POST request with retry logic and circuit breaker.

        Args:
            endpoint: API endpoint path.
            data: Form data payload.
            max_retries: Maximum number of retries. Uses config default if None.

        Returns:
            Parsed JSON response.

        Raises:
            APIException: For API-related errors.
            ConnectionException: For connection issues.
        """
        if not self._client:
            raise ConnectionException("HTTP client not initialized. Use async context manager.")

        # Check circuit breaker
        if self.circuit_breaker and not self.circuit_breaker.can_execute():
            raise ConnectionException("Circuit breaker is open. Service may be unavailable.")

        max_retries = max_retries or self.api_settings.retry_attempts
        url = f"{self.api_settings.base_url}{endpoint}"

        last_exception = None

        for attempt in range(max_retries + 1):
            try:
                self.logger.debug(f"Attempting request to {url} (attempt {attempt + 1})")

                response = await self._client.post(url, data=data)

                # Check for successful response
                if response.status_code == 200:
                    try:
                        json_data = response.json()

                        # Record success for circuit breaker
                        if self.circuit_breaker:
                            self.circuit_breaker.record_success()

                        self.logger.debug(f"Successful response from {url}")
                        return json_data

                    except json.JSONDecodeError as e:
                        error_msg = f"Failed to decode JSON response from {url}: {e}"
                        self.logger.error(f"{error_msg}. Response text: {response.text[:500]}...")
                        raise APIException(
                            error_msg,
                            status_code=response.status_code,
                            response_data={"text_preview": response.text[:500]},
                        )

                # Handle different HTTP status codes
                elif response.status_code == 429:
                    raise RateLimitException(
                        f"Rate limit exceeded for {url}",
                        status_code=response.status_code,
                        response_data={"text": response.text},
                    )
                elif response.status_code in (401, 403):
                    raise AuthenticationException(
                        f"Authentication failed for {url}",
                        status_code=response.status_code,
                        response_data={"text": response.text},
                    )
                else:
                    error_msg = f"HTTP {response.status_code} error for {url}"
                    last_exception = APIException(
                        error_msg, status_code=response.status_code, response_data={"text": response.text[:500]}
                    )

            except httpx.RequestError as e:
                error_msg = f"Request failed for {url}: {e}"
                self.logger.warning(error_msg)
                last_exception = ConnectionException(error_msg, details={"attempt": attempt + 1})

            except (RateLimitException, AuthenticationException):
                # Don't retry for these errors
                if self.circuit_breaker:
                    self.circuit_breaker.record_failure()
                raise

            except Exception as e:
                error_msg = f"Unexpected error for {url}: {e}"
                self.logger.error(error_msg)
                last_exception = APIException(error_msg, details={"attempt": attempt + 1})

            # Wait before retrying (exponential backoff)
            if attempt < max_retries:
                delay = self.api_settings.retry_delay * (2**attempt)
                self.logger.info(f"Retrying in {delay:.1f} seconds...")
                await asyncio.sleep(delay)

        # All retries exhausted, record failure and raise last exception
        if self.circuit_breaker:
            self.circuit_breaker.record_failure()

        if last_exception:
            raise last_exception
        else:
            raise ConnectionException(f"All retry attempts exhausted for {url}")

    @property
    def is_circuit_open(self) -> bool:
        """Check if circuit breaker is open."""
        return self.circuit_breaker and self.circuit_breaker.state == "open"

"""Kuro BBS API client with domain-specific methods."""

from typing import Any

from ...core.config import APISettings
from ...core.config import get_settings
from ...core.exceptions import APIException
from ...core.exceptions import DataNotFoundException
from ...core.logging_config import LoggerMixin
from .http_client import HTTPClient


class KuroAPIClient(LoggerMixin):
    """Kuro BBS Wiki API client with enhanced error handling."""

    def __init__(
        self,
        http_client: HTTPClient | None = None,
        settings: APISettings | None = None,
    ):
        """Initialize Kuro API client.

        Args:
            http_client: Optional HTTP client. If None, will create one from settings.
            settings: Optional API settings. If None, will use global settings.
        """
        if settings is None:
            app_settings = get_settings()
            settings = app_settings.api

        self.settings = settings
        self._http_client = http_client
        self._owns_http_client = http_client is None

    async def __aenter__(self) -> "KuroAPIClient":
        """Async context manager entry."""
        if self._http_client is None:
            app_settings = get_settings()
            self._http_client = HTTPClient(api_settings=self.settings, http_settings=app_settings.http_client)
            self._owns_http_client = True

        # Always initialize the HTTP client if it exists
        if self._http_client:
            await self._http_client.__aenter__()

        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        """Async context manager exit."""
        if self._http_client:
            await self._http_client.__aexit__(exc_type, exc_value, traceback)

    async def fetch_character_list(self) -> list[dict[str, Any]]:
        """Fetch list of characters from Kuro BBS API.

        Returns:
            List of character records.

        Raises:
            APIException: If request fails or response structure is invalid.
        """
        self.logger.info("Fetching character list")

        form_data = {
            "catalogueId": self.settings.character_catalogue_id,
            "page": self.settings.default_page,
            "limit": self.settings.default_limit,
        }

        try:
            response_data = await self._http_client.post_with_retry("/getPage", form_data)

            # Validate response structure
            if not self._validate_list_response(response_data):
                raise APIException("Invalid response structure for character list", response_data=response_data)

            records = response_data["data"]["results"]["records"]
            self.logger.info(f"Successfully fetched {len(records)} characters")
            return records

        except Exception as e:
            self.logger.error(f"Failed to fetch character list: {e}")
            if isinstance(e, APIException):
                raise
            else:
                raise APIException(f"Character list fetch failed: {e}")

    async def fetch_artifacts_list(self) -> list[dict[str, Any]]:
        """Fetch list of artifacts from Kuro BBS API.

        Returns:
            List of artifact records.

        Raises:
            APIException: If request fails or response structure is invalid.
        """
        self.logger.info("Fetching artifacts list")

        form_data = {
            "catalogueId": self.settings.artifacts_catalogue_id,
            "page": self.settings.default_page,
            "limit": self.settings.default_limit,
        }

        try:
            response_data = await self._http_client.post_with_retry("/getPage", form_data)

            # Validate response structure
            if not self._validate_list_response(response_data):
                raise APIException("Invalid response structure for artifacts list", response_data=response_data)

            records = response_data["data"]["results"]["records"]
            self.logger.info(f"Successfully fetched {len(records)} artifacts")
            return records

        except Exception as e:
            self.logger.error(f"Failed to fetch artifacts list: {e}")
            if isinstance(e, APIException):
                raise
            else:
                raise APIException(f"Artifacts list fetch failed: {e}")

    async def fetch_entry_detail(self, entry_id: str) -> dict[str, Any]:
        """Fetch detailed entry information by ID.

        Args:
            entry_id: The entry ID to fetch.

        Returns:
            Entry detail data.

        Raises:
            DataNotFoundException: If entry is not found.
            APIException: If request fails or response structure is invalid.
        """
        if not entry_id:
            raise ValueError("Entry ID cannot be empty")

        self.logger.info(f"Fetching entry detail for ID: {entry_id}")

        form_data = {"id": entry_id}

        try:
            response_data = await self._http_client.post_with_retry("/getEntryDetail", form_data)

            # Validate response structure
            if not self._validate_detail_response(response_data):
                # Check if it's a "not found" case
                if response_data.get("code") == 404 or "not found" in str(response_data).lower():
                    raise DataNotFoundException("entry", entry_id)

                raise APIException(
                    f"Invalid response structure for entry detail {entry_id}", response_data=response_data
                )

            content = response_data["data"]["content"]
            self.logger.info(f"Successfully fetched entry detail for ID: {entry_id}")
            return content

        except DataNotFoundException:
            raise
        except Exception as e:
            self.logger.error(f"Failed to fetch entry detail for {entry_id}: {e}")
            if isinstance(e, APIException):
                raise
            else:
                raise APIException(f"Entry detail fetch failed for {entry_id}: {e}")

    def _validate_list_response(self, response_data: dict[str, Any]) -> bool:
        """Validate structure of list response.

        Args:
            response_data: Response data to validate.

        Returns:
            True if structure is valid, False otherwise.
        """
        try:
            return (
                "data" in response_data
                and "results" in response_data["data"]
                and "records" in response_data["data"]["results"]
                and isinstance(response_data["data"]["results"]["records"], list)
            )
        except (KeyError, TypeError):
            return False

    def _validate_detail_response(self, response_data: dict[str, Any]) -> bool:
        """Validate structure of detail response.

        Args:
            response_data: Response data to validate.

        Returns:
            True if structure is valid, False otherwise.
        """
        try:
            return (
                "data" in response_data
                and "content" in response_data["data"]
                and isinstance(response_data["data"]["content"], dict)
            )
        except (KeyError, TypeError):
            return False


# Factory function for dependency injection
def create_kuro_api_client(
    http_client: HTTPClient | None = None,
    settings: APISettings | None = None,
) -> KuroAPIClient:
    """Factory function to create KuroAPIClient.

    Args:
        http_client: Optional HTTP client.
        settings: Optional API settings.

    Returns:
        Configured KuroAPIClient instance.
    """
    return KuroAPIClient(http_client=http_client, settings=settings)

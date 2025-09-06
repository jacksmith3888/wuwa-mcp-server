"""Custom exception hierarchy for WuWa MCP Server."""

from typing import Any


class WuWaException(Exception):
    """Base exception for all WuWa MCP Server errors."""

    def __init__(
        self,
        message: str,
        code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code or self.__class__.__name__
        self.details = details or {}

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"

    def to_dict(self) -> dict[str, Any]:
        """Convert exception to dictionary for logging/serialization."""
        return {
            "error_type": self.__class__.__name__,
            "code": self.code,
            "message": self.message,
            "details": self.details,
        }


class APIException(WuWaException):
    """Base exception for API-related errors."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_data: dict[str, Any] | None = None,
        **kwargs,
    ) -> None:
        # Remove 'details' from kwargs to avoid duplicate parameter
        details = kwargs.pop("details", {})
        if status_code:
            details["status_code"] = status_code
        if response_data:
            details["response_data"] = response_data

        super().__init__(message, details=details, **kwargs)
        self.status_code = status_code
        self.response_data = response_data


class ConnectionException(APIException):
    """Raised when API connection fails."""

    pass


class RateLimitException(APIException):
    """Raised when API rate limit is exceeded."""

    pass


class AuthenticationException(APIException):
    """Raised when API authentication fails."""

    pass


class DataNotFoundException(APIException):
    """Raised when requested data is not found."""

    def __init__(
        self,
        resource_type: str,
        resource_id: str,
        **kwargs,
    ) -> None:
        message = f"{resource_type} with ID '{resource_id}' not found"
        details = kwargs.get("details", {})
        details.update({"resource_type": resource_type, "resource_id": resource_id})
        super().__init__(message, details=details, code=kwargs.get("code"))
        self.resource_type = resource_type
        self.resource_id = resource_id


class ParsingException(WuWaException):
    """Base exception for parsing-related errors."""

    pass


class HTMLParsingException(ParsingException):
    """Raised when HTML parsing fails."""

    def __init__(
        self,
        message: str,
        html_content: str | None = None,
        **kwargs,
    ) -> None:
        details = kwargs.get("details", {})
        if html_content:
            # Store only first 500 chars to avoid huge logs
            details["html_preview"] = html_content[:500]

        super().__init__(message, details=details, **kwargs)
        self.html_content = html_content


class DataStructureException(ParsingException):
    """Raised when data structure is unexpected."""

    def __init__(
        self,
        message: str,
        expected_structure: str | None = None,
        actual_data: dict[str, Any] | None = None,
        **kwargs,
    ) -> None:
        details = kwargs.get("details", {})
        if expected_structure:
            details["expected_structure"] = expected_structure
        if actual_data:
            # Only store keys to avoid huge logs
            details["actual_keys"] = (
                list(actual_data.keys()) if isinstance(actual_data, dict) else str(type(actual_data))
            )

        super().__init__(message, details=details, **kwargs)
        self.expected_structure = expected_structure
        self.actual_data = actual_data


class ValidationException(WuWaException):
    """Raised when data validation fails."""

    def __init__(
        self,
        field: str,
        value: Any,
        reason: str,
        **kwargs,
    ) -> None:
        message = f"Validation failed for field '{field}': {reason}"
        details = {"field": field, "value": str(value), "reason": reason}
        super().__init__(message, details=details, **kwargs)
        self.field = field
        self.value = value
        self.reason = reason


class ConfigurationException(WuWaException):
    """Raised when configuration is invalid."""

    pass


class ServiceException(WuWaException):
    """Base exception for service-layer errors."""

    pass


class MarkdownGenerationException(ServiceException):
    """Raised when markdown generation fails."""

    pass

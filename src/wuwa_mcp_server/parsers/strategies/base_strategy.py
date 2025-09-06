"""Base parsing strategy implementation."""

from abc import ABC
from abc import abstractmethod
from typing import Any

from ...core.interfaces import BaseParsingStrategy as IBaseParsingStrategy
from ...core.logging_config import LoggerMixin
from ...domain.value_objects import ContentType


class BaseParsingStrategy(IBaseParsingStrategy, LoggerMixin, ABC):
    """Base class for content parsing strategies."""

    def __init__(self):
        """Initialize the base strategy."""
        pass

    @abstractmethod
    def can_handle(self, content_type: str) -> bool:
        """Check if this strategy can handle the content type."""
        pass

    @abstractmethod
    def parse(self, content_data: dict[str, Any]) -> dict[str, Any]:
        """Parse content using this strategy."""
        pass

    def get_supported_content_types(self) -> list[ContentType]:
        """Get list of supported content types.

        Override in subclasses to specify which content types are supported.
        """
        return []

    def validate_content_data(self, content_data: dict[str, Any]) -> bool:
        """Validate that content data has required structure.

        Args:
            content_data: Content data to validate.

        Returns:
            True if valid, False otherwise.
        """
        return isinstance(content_data, dict) and "title" in content_data and "modules" in content_data

    def create_result_structure(self, title: str) -> dict[str, Any]:
        """Create base result structure.

        Args:
            title: Title for the result.

        Returns:
            Base result structure.
        """
        return {"title": title, "modules": {}}

    def extract_title(self, content_data: dict[str, Any]) -> str:
        """Extract title from content data.

        Args:
            content_data: Content data.

        Returns:
            Title string.
        """
        return content_data.get("title", "Untitled")

    def filter_modules_by_types(
        self, modules_data: list[dict[str, Any]], target_types: list[str]
    ) -> list[dict[str, Any]]:
        """Filter modules by target types.

        Args:
            modules_data: Raw modules data.
            target_types: List of target module types to include.

        Returns:
            Filtered modules list.
        """
        filtered = []
        for module in modules_data:
            module_title = module.get("title", "")
            if module_title in target_types:
                filtered.append(module)
        return filtered

    def safe_get_nested(self, data: dict[str, Any], keys: list[str], default: Any = None) -> Any:
        """Safely get nested dictionary value.

        Args:
            data: Dictionary to search in.
            keys: List of keys for nested access.
            default: Default value if not found.

        Returns:
            Found value or default.
        """
        current = data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return current

"""Base repository implementation."""

from abc import ABC
from abc import abstractmethod
from typing import Any

from ...core.exceptions import DataNotFoundException
from ...core.interfaces import BaseRepository as IBaseRepository
from ...core.logging_config import LoggerMixin


class BaseRepository(IBaseRepository, LoggerMixin, ABC):
    """Base repository with common functionality."""

    def __init__(self, api_client):
        """Initialize repository with API client.

        Args:
            api_client: API client for data fetching.
        """
        self.api_client = api_client

    @abstractmethod
    async def find_by_name(self, name: str) -> dict[str, Any] | None:
        """Find item by name. Must be implemented by subclasses."""
        pass

    async def get_all(self) -> list[dict[str, Any]]:
        """Get all items. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement get_all method")

    def _find_item_by_name(
        self,
        items: list[dict[str, Any]],
        name: str,
        resource_type: str,
    ) -> dict[str, Any]:
        """Helper method to find item by name in a list.

        Args:
            items: List of items to search in.
            name: Name to search for.
            resource_type: Type of resource for error messages.

        Returns:
            Found item.

        Raises:
            DataNotFoundException: If item is not found.
        """
        # Case-insensitive search
        name_lower = name.lower()

        for item in items:
            item_name = item.get("name", "")
            if item_name.lower() == name_lower:
                self.logger.debug(f"Found {resource_type}: {item_name}")
                return item

        # Log available names for debugging
        available_names = [item.get("name", "N/A") for item in items[:10]]  # First 10 for logs
        self.logger.warning(f"{resource_type} '{name}' not found. Available (first 10): {available_names}")

        raise DataNotFoundException(resource_type, name)

    def _extract_entry_id(self, item: dict[str, Any], resource_type: str) -> str:
        """Extract entry ID from item.

        Args:
            item: Item data.
            resource_type: Type of resource for error messages.

        Returns:
            Entry ID.

        Raises:
            DataNotFoundException: If entry ID is missing.
        """
        content = item.get("content", {})
        entry_id = content.get("linkId")

        if not entry_id:
            item_name = item.get("name", "Unknown")
            self.logger.error(f"No entry ID found for {resource_type}: {item_name}")
            raise DataNotFoundException(f"{resource_type}_entry_id", item_name)

        return entry_id

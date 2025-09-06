"""Character repository implementation."""

from typing import Any

from ...core.interfaces import CharacterRepositoryProtocol
from ...domain.entities import Character
from ...domain.value_objects import CharacterId
from .base_repository import BaseRepository


class CharacterRepository(BaseRepository, CharacterRepositoryProtocol):
    """Repository for character data access."""

    async def find_by_name(self, name: str) -> dict[str, Any] | None:
        """Find character by name.

        Args:
            name: Character name to search for.

        Returns:
            Character data if found, None otherwise.
        """
        try:
            characters = await self.get_character_list()
            character_data = self._find_item_by_name(characters, name, "character")

            # Get entry ID
            entry_id = self._extract_entry_id(character_data, "character")

            # Fetch detailed character data
            detail_data = await self.get_character_detail(entry_id)

            return detail_data

        except Exception as e:
            self.logger.error(f"Failed to find character by name '{name}': {e}")
            return None

    async def get_character_list(self) -> list[dict[str, Any]]:
        """Get list of all characters.

        Returns:
            List of character metadata.

        Raises:
            APIException: If request fails.
        """
        self.logger.info("Fetching character list from API")
        async with self.api_client as client:
            return await client.fetch_character_list()

    async def get_character_detail(self, entry_id: str) -> dict[str, Any] | None:
        """Get character detail by entry ID.

        Args:
            entry_id: Character entry ID.

        Returns:
            Character detail data if found.

        Raises:
            APIException: If request fails.
        """
        if not entry_id:
            raise ValueError("Entry ID cannot be empty")

        self.logger.info(f"Fetching character detail for entry_id: {entry_id}")
        async with self.api_client as client:
            return await client.fetch_entry_detail(entry_id)

    async def get_all(self) -> list[dict[str, Any]]:
        """Get all characters (alias for get_character_list)."""
        async with self.api_client as client:
            return await client.fetch_character_list()

    def create_character_entity(
        self, name: str, entry_id: str, detail_data: dict[str, Any] | None = None
    ) -> Character:
        """Create Character entity from data.

        Args:
            name: Character name.
            entry_id: Character entry ID.
            detail_data: Optional detailed character data.

        Returns:
            Character entity.
        """
        character_id = CharacterId(entry_id=entry_id, name=name)
        character = Character(id=character_id)

        # TODO: Parse detail_data and populate character fields
        # This would involve using the content parser to extract:
        # - basic_info
        # - modules
        # - skills
        # - strategy_item_id

        return character

    async def find_character_entity_by_name(self, name: str) -> Character | None:
        """Find character entity by name.

        Args:
            name: Character name.

        Returns:
            Character entity if found.
        """
        try:
            # First, get the character list to find the entry
            characters = await self.get_character_list()
            character_data = self._find_item_by_name(characters, name, "character")

            # Extract entry ID
            entry_id = self._extract_entry_id(character_data, "character")

            # Get detailed data
            detail_data = await self.get_character_detail(entry_id)

            # Create entity
            return self.create_character_entity(name, entry_id, detail_data)

        except Exception as e:
            self.logger.error(f"Failed to find character entity '{name}': {e}")
            return None


# Factory function
def create_character_repository(api_client) -> CharacterRepository:
    """Create character repository.

    Args:
        api_client: API client for data fetching.

    Returns:
        CharacterRepository instance.
    """
    return CharacterRepository(api_client)

"""Artifact repository implementation."""

from typing import Any

from ...core.interfaces import ArtifactRepositoryProtocol
from ...domain.entities import Artifact
from ...domain.value_objects import ArtifactId
from .base_repository import BaseRepository


class ArtifactRepository(BaseRepository, ArtifactRepositoryProtocol):
    """Repository for artifact data access."""

    async def find_by_name(self, name: str) -> dict[str, Any] | None:
        """Find artifact by name.

        Args:
            name: Artifact name to search for.

        Returns:
            Artifact data if found, None otherwise.
        """
        try:
            artifacts = await self.get_artifact_list()
            artifact_data = self._find_item_by_name(artifacts, name, "artifact")

            # Get entry ID
            entry_id = self._extract_entry_id(artifact_data, "artifact")

            # Fetch detailed artifact data
            detail_data = await self.get_artifact_detail(entry_id)

            return detail_data

        except Exception as e:
            self.logger.error(f"Failed to find artifact by name '{name}': {e}")
            return None

    async def get_artifact_list(self) -> list[dict[str, Any]]:
        """Get list of all artifacts.

        Returns:
            List of artifact metadata.

        Raises:
            APIException: If request fails.
        """
        self.logger.info("Fetching artifact list from API")
        async with self.api_client:
            return await self.api_client.fetch_artifacts_list()

    async def get_artifact_detail(self, entry_id: str) -> dict[str, Any] | None:
        """Get artifact detail by entry ID.

        Args:
            entry_id: Artifact entry ID.

        Returns:
            Artifact detail data if found.

        Raises:
            APIException: If request fails.
        """
        if not entry_id:
            raise ValueError("Entry ID cannot be empty")

        self.logger.info(f"Fetching artifact detail for entry_id: {entry_id}")
        async with self.api_client:
            return await self.api_client.fetch_entry_detail(entry_id)

    async def get_all(self) -> list[dict[str, Any]]:
        """Get all artifacts (alias for get_artifact_list)."""
        return await self.get_artifact_list()

    def create_artifact_entity(self, name: str, entry_id: str, detail_data: dict[str, Any] | None = None) -> Artifact:
        """Create Artifact entity from data.

        Args:
            name: Artifact name.
            entry_id: Artifact entry ID.
            detail_data: Optional detailed artifact data.

        Returns:
            Artifact entity.
        """
        artifact_id = ArtifactId(entry_id=entry_id, name=name)
        artifact = Artifact(id=artifact_id)

        # TODO: Parse detail_data and populate artifact fields
        # This would involve using the content parser to extract:
        # - set_effects
        # - modules
        # - echo_types

        return artifact

    async def find_artifact_entity_by_name(self, name: str) -> Artifact | None:
        """Find artifact entity by name.

        Args:
            name: Artifact name.

        Returns:
            Artifact entity if found.
        """
        try:
            # First, get the artifact list to find the entry
            artifacts = await self.get_artifact_list()
            artifact_data = self._find_item_by_name(artifacts, name, "artifact")

            # Extract entry ID
            entry_id = self._extract_entry_id(artifact_data, "artifact")

            # Get detailed data
            detail_data = await self.get_artifact_detail(entry_id)

            # Create entity
            return self.create_artifact_entity(name, entry_id, detail_data)

        except Exception as e:
            self.logger.error(f"Failed to find artifact entity '{name}': {e}")
            return None

    async def search_artifacts_by_echo_type(self, echo_type: str) -> list[dict[str, Any]]:
        """Search artifacts that contain specific echo type.

        Args:
            echo_type: Echo type to search for.

        Returns:
            List of matching artifacts.
        """
        artifacts = await self.get_artifact_list()
        matching = []

        for artifact in artifacts:
            # This would require parsing the artifact data to check echo types
            # For now, return empty list - implement when parser is ready
            pass

        return matching


# Factory function
def create_artifact_repository(api_client) -> ArtifactRepository:
    """Create artifact repository.

    Args:
        api_client: API client for data fetching.

    Returns:
        ArtifactRepository instance.
    """
    return ArtifactRepository(api_client)

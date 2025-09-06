"""Artifact service for business logic encapsulation."""

import asyncio
from typing import Any

from ..core.exceptions import DataNotFoundException
from ..core.exceptions import ServiceException
from ..core.interfaces import ArtifactServiceProtocol
from ..core.logging_config import LoggerMixin
from ..infrastructure.repositories import ArtifactRepository
from ..parsers.content_parser import StrategyBasedContentParser


class ArtifactService(ArtifactServiceProtocol, LoggerMixin):
    """Service for artifact-related business operations."""

    def __init__(
        self,
        artifact_repository: ArtifactRepository,
        content_parser: StrategyBasedContentParser,
        markdown_service: "MarkdownService",  # Forward reference
    ):
        """Initialize artifact service.

        Args:
            artifact_repository: Repository for artifact data access.
            content_parser: Content parser for processing raw data.
            markdown_service: Service for markdown generation.
        """
        self.artifact_repository = artifact_repository
        self.content_parser = content_parser
        self.markdown_service = markdown_service

    async def get_artifact_info(self, artifact_name: str) -> str:
        """Get comprehensive artifact information.

        Args:
            artifact_name: Name of the artifact set to query.

        Returns:
            Markdown formatted artifact information.

        Raises:
            ServiceException: If artifact retrieval fails.
        """
        try:
            self.logger.info(f"Getting artifact info for: {artifact_name}")

            # Get artifact raw data
            artifact_raw_data = await self._get_artifact_data(artifact_name)

            # Parse artifact content
            artifact_parsed_data = await asyncio.to_thread(
                self.content_parser.parse_artifact_content, artifact_raw_data
            )

            # Generate markdown
            artifact_markdown = self.markdown_service.generate_artifact_markdown(artifact_parsed_data)

            if not artifact_markdown.strip():
                self.logger.warning(f"Generated empty artifact info for: {artifact_name}")
                return f"成功获取 '{artifact_name}' 的声骸数据，但解析后的内容无法生成有效的 Markdown。"

            self.logger.info(f"Successfully generated artifact info for: {artifact_name}")
            return artifact_markdown

        except DataNotFoundException:
            error_msg = f"Artifact set '{artifact_name}' not found"
            self.logger.error(error_msg)
            return f"错误：未找到名为 '{artifact_name}' 的声骸套装。"

        except Exception as e:
            self.logger.error(f"Failed to get artifact info for {artifact_name}: {e}")
            raise ServiceException(f"Artifact info retrieval failed: {e}")

    async def _get_artifact_data(self, artifact_name: str) -> dict[str, Any]:
        """Get artifact raw data from repository.

        Args:
            artifact_name: Name of the artifact set.

        Returns:
            Raw artifact data.

        Raises:
            DataNotFoundException: If artifact not found.
            ServiceException: If data retrieval fails.
        """
        try:
            artifact_data = await self.artifact_repository.find_by_name(artifact_name)

            if not artifact_data:
                raise DataNotFoundException("artifact", artifact_name)

            return artifact_data

        except DataNotFoundException:
            raise
        except Exception as e:
            self.logger.error(f"Failed to get artifact data for {artifact_name}: {e}")
            raise ServiceException(f"Artifact data retrieval failed: {e}")


# Factory function for dependency injection
def create_artifact_service(
    artifact_repository: ArtifactRepository,
    content_parser: StrategyBasedContentParser,
    markdown_service: "MarkdownService",
) -> ArtifactService:
    """Create artifact service.

    Args:
        artifact_repository: Artifact repository.
        content_parser: Content parser.
        markdown_service: Markdown service.

    Returns:
        ArtifactService instance.
    """
    return ArtifactService(artifact_repository, content_parser, markdown_service)

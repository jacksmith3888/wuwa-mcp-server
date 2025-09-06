"""Character service for business logic encapsulation."""

import asyncio
import re
from typing import Any

from ..core.exceptions import DataNotFoundException
from ..core.exceptions import ServiceException
from ..core.interfaces import CharacterServiceProtocol
from ..core.logging_config import LoggerMixin
from ..infrastructure.repositories import CharacterRepository
from ..parsers.content_parser import StrategyBasedContentParser


class CharacterService(CharacterServiceProtocol, LoggerMixin):
    """Service for character-related business operations."""

    def __init__(
        self,
        character_repository: CharacterRepository,
        content_parser: StrategyBasedContentParser,
        markdown_service: "MarkdownService",  # Forward reference
    ):
        """Initialize character service.

        Args:
            character_repository: Repository for character data access.
            content_parser: Content parser for processing raw data.
            markdown_service: Service for markdown generation.
        """
        self.character_repository = character_repository
        self.content_parser = content_parser
        self.markdown_service = markdown_service

    async def get_character_info(self, character_name: str) -> str:
        """Get comprehensive character information including strategy.

        Args:
            character_name: Name of the character to query.

        Returns:
            Markdown formatted character information.

        Raises:
            ServiceException: If character retrieval fails.
        """
        try:
            self.logger.info(f"Getting character info for: {character_name}")

            # Get character raw data
            character_raw_data = await self._get_character_data(character_name)

            # Extract strategy item ID for parallel processing
            strategy_item_id = self._extract_strategy_item_id(character_raw_data)

            # Parallel processing: parse profile and fetch strategy
            profile_task = asyncio.create_task(
                asyncio.to_thread(self.content_parser.parse_main_content, character_raw_data)
            )

            strategy_task = None
            if strategy_item_id:
                strategy_task = asyncio.create_task(self._fetch_strategy_content(strategy_item_id))

            # Wait for profile parsing
            character_profile_data = await profile_task

            # Generate markdown for profile
            character_markdown = self.markdown_service.generate_character_markdown(
                character_profile_data, include_strategy=False
            )

            # Process strategy if available
            strategy_markdown = ""
            if strategy_task:
                try:
                    strategy_raw_data = await strategy_task
                    if strategy_raw_data:
                        strategy_parsed = await asyncio.to_thread(
                            self.content_parser.parse_strategy_content, strategy_raw_data
                        )
                        strategy_markdown = self.markdown_service.generate_strategy_markdown(strategy_parsed)
                except Exception as e:
                    self.logger.warning(f"Failed to process strategy content: {e}")

            # Combine results
            combined_markdown = character_markdown
            if strategy_markdown:
                combined_markdown += "\n\n" + strategy_markdown

            # Add strategy link if available
            if strategy_item_id:
                link_markdown = self._generate_strategy_link_markdown(strategy_item_id)
                combined_markdown += "\n\n" + link_markdown

            self.logger.info(f"Successfully generated character info for: {character_name}")
            return combined_markdown

        except DataNotFoundException:
            error_msg = f"Character '{character_name}' not found"
            self.logger.error(error_msg)
            return f"错误：未找到名为 '{character_name}' 的角色。"

        except Exception as e:
            self.logger.error(f"Failed to get character info for {character_name}: {e}")
            raise ServiceException(f"Character info retrieval failed: {e}")

    async def get_character_profile(self, character_name: str) -> str:
        """Get character profile information only.

        Args:
            character_name: Name of the character to query.

        Returns:
            Markdown formatted character profile.

        Raises:
            ServiceException: If character profile retrieval fails.
        """
        try:
            self.logger.info(f"Getting character profile for: {character_name}")

            # Get character raw data
            character_raw_data = await self._get_character_data(character_name)

            # Parse profile content
            character_profile_data = await asyncio.to_thread(
                self.content_parser.parse_character_profile, character_raw_data
            )

            # Generate markdown
            profile_markdown = self.markdown_service.generate_character_markdown(
                character_profile_data, include_strategy=False
            )

            if not profile_markdown.strip():
                self.logger.warning(f"Generated empty profile for: {character_name}")
                return f"成功获取 '{character_name}' 的档案数据，但解析后的内容无法生成有效的 Markdown。"

            self.logger.info(f"Successfully generated character profile for: {character_name}")
            return profile_markdown

        except DataNotFoundException:
            error_msg = f"Character '{character_name}' not found"
            self.logger.error(error_msg)
            return f"错误：未找到名为 '{character_name}' 的角色。"

        except Exception as e:
            self.logger.error(f"Failed to get character profile for {character_name}: {e}")
            raise ServiceException(f"Character profile retrieval failed: {e}")

    async def _get_character_data(self, character_name: str) -> dict[str, Any]:
        """Get character raw data from repository.

        Args:
            character_name: Name of the character.

        Returns:
            Raw character data.

        Raises:
            DataNotFoundException: If character not found.
            ServiceException: If data retrieval fails.
        """
        try:
            character_data = await self.character_repository.find_by_name(character_name)

            if not character_data:
                raise DataNotFoundException("character", character_name)

            return character_data

        except DataNotFoundException:
            raise
        except Exception as e:
            self.logger.error(f"Failed to get character data for {character_name}: {e}")
            raise ServiceException(f"Character data retrieval failed: {e}")

    def _extract_strategy_item_id(self, character_raw_data: dict[str, Any]) -> str | None:
        """Extract strategy item ID from character data.

        Args:
            character_raw_data: Raw character data.

        Returns:
            Strategy item ID if found, None otherwise.
        """
        try:
            modules = character_raw_data.get("modules", [])

            for module in modules:
                module_title = module.get("title", "")
                if module_title in ["角色攻略", "角色养成推荐"]:
                    components = module.get("components", [])
                    for component in components:
                        content = component.get("content", "")
                        if content:
                            item_id = self._extract_item_id_from_html(content)
                            if item_id:
                                self.logger.debug(f"Extracted strategy item ID: {item_id}")
                                return item_id

            self.logger.debug("No strategy item ID found")
            return None

        except Exception as e:
            self.logger.warning(f"Failed to extract strategy item ID: {e}")
            return None

    def _extract_item_id_from_html(self, html_content: str) -> str | None:
        """Extract item ID from HTML content using regex.

        Args:
            html_content: HTML content to search.

        Returns:
            Extracted item ID or None.
        """
        if not html_content:
            return None

        pattern = r"https://wiki\.kurobbs\.com/mc/item/(\d+)"
        match = re.search(pattern, html_content)
        return match.group(1) if match else None

    async def _fetch_strategy_content(self, strategy_item_id: str) -> dict[str, Any] | None:
        """Fetch strategy content from API.

        Args:
            strategy_item_id: Strategy item ID.

        Returns:
            Strategy content data or None if failed.
        """
        try:
            self.logger.info(f"Fetching strategy content for ID: {strategy_item_id}")

            # Use the same API client as the repository
            strategy_data = await self.character_repository.api_client.fetch_entry_detail(strategy_item_id)

            if strategy_data:
                self.logger.debug("Strategy content fetched successfully")
            else:
                self.logger.warning(f"No strategy content found for ID: {strategy_item_id}")

            return strategy_data

        except Exception as e:
            self.logger.error(f"Failed to fetch strategy content: {e}")
            return None

    def _generate_strategy_link_markdown(self, strategy_item_id: str) -> str:
        """Generate markdown for strategy link.

        Args:
            strategy_item_id: Strategy item ID.

        Returns:
            Markdown formatted strategy link.
        """
        url = f"https://wiki.kurobbs.com/mc/item/{strategy_item_id}"
        return f"""## Character Strategy Link

- Strategy Item ID: {strategy_item_id}
- [View Strategy]({url})"""


# Factory function for dependency injection
def create_character_service(
    character_repository: CharacterRepository,
    content_parser: StrategyBasedContentParser,
    markdown_service: "MarkdownService",
) -> CharacterService:
    """Create character service.

    Args:
        character_repository: Character repository.
        content_parser: Content parser.
        markdown_service: Markdown service.

    Returns:
        CharacterService instance.
    """
    return CharacterService(character_repository, content_parser, markdown_service)

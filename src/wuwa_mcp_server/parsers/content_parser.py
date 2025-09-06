"""Strategy-based content parser with improved architecture."""

from typing import Any

from ..core.exceptions import ParsingException
from ..core.logging_config import LoggerMixin
from ..domain.value_objects import ContentType
from .html_converter import HTMLToMarkdownConverter
from .strategies import ArtifactStrategy
from .strategies import BaseParsingStrategy
from .strategies import CharacterDataStrategy
from .strategies import CharacterProfileStrategy
from .strategies import StrategyContentStrategy


class StrategyBasedContentParser(LoggerMixin):
    """Content parser using strategy pattern for different content types."""

    def __init__(self, html_converter: HTMLToMarkdownConverter | None = None):
        """Initialize the parser with strategies.

        Args:
            html_converter: HTML converter instance. Creates one if None.
        """
        self.html_converter = html_converter or HTMLToMarkdownConverter()
        self.strategies: list[BaseParsingStrategy] = []
        self._register_default_strategies()

    def _register_default_strategies(self) -> None:
        """Register default parsing strategies."""
        self.strategies = [
            CharacterDataStrategy(self.html_converter),
            CharacterProfileStrategy(self.html_converter),
            ArtifactStrategy(self.html_converter),
            StrategyContentStrategy(self.html_converter),
        ]
        self.logger.info(f"Registered {len(self.strategies)} parsing strategies")

    def register_strategy(self, strategy: BaseParsingStrategy) -> None:
        """Register a new parsing strategy.

        Args:
            strategy: Strategy to register.
        """
        self.strategies.append(strategy)
        self.logger.info(f"Registered strategy: {strategy.__class__.__name__}")

    def parse_main_content(self, content_data: dict[str, Any]) -> dict[str, Any]:
        """Parse main content with automatic strategy selection.

        Args:
            content_data: Raw content data from API.

        Returns:
            Parsed content structure.

        Raises:
            ParsingException: If parsing fails.
        """
        try:
            self.logger.info("Parsing main content")

            # Determine which strategies to use based on content
            modules_data = content_data.get("modules", [])
            module_types = [module.get("title", "") for module in modules_data]

            self.logger.debug(f"Found module types: {module_types}")

            # Use multi-strategy approach for main content
            strategies_to_use = self._select_strategies_for_main_content(module_types)

            return self._parse_with_strategies(content_data, strategies_to_use)

        except Exception as e:
            self.logger.error(f"Failed to parse main content: {e}")
            raise ParsingException(f"Main content parsing failed: {e}")

    def parse_character_profile(self, content_data: dict[str, Any]) -> dict[str, Any]:
        """Parse character profile content.

        Args:
            content_data: Raw content data from API.

        Returns:
            Parsed content structure.

        Raises:
            ParsingException: If parsing fails.
        """
        try:
            self.logger.info("Parsing character profile")

            # Use only profile strategy
            profile_strategy = self._find_strategy(CharacterProfileStrategy)
            if not profile_strategy:
                raise ParsingException("Character profile strategy not found")

            return profile_strategy.parse(content_data)

        except Exception as e:
            self.logger.error(f"Failed to parse character profile: {e}")
            raise ParsingException(f"Character profile parsing failed: {e}")

    def parse_strategy_content(self, content_data: dict[str, Any]) -> dict[str, Any]:
        """Parse strategy content without module filtering.

        Args:
            content_data: Raw content data from API.

        Returns:
            Parsed content structure.

        Raises:
            ParsingException: If parsing fails.
        """
        try:
            self.logger.info("Parsing strategy content")

            # Use strategy content parser
            strategy_parser = self._find_strategy(StrategyContentStrategy)
            if not strategy_parser:
                raise ParsingException("Strategy content parser not found")

            return strategy_parser.parse(content_data)

        except Exception as e:
            self.logger.error(f"Failed to parse strategy content: {e}")
            raise ParsingException(f"Strategy content parsing failed: {e}")

    def parse_artifact_content(self, content_data: dict[str, Any]) -> dict[str, Any]:
        """Parse artifact content.

        Args:
            content_data: Raw content data from API.

        Returns:
            Parsed content structure.

        Raises:
            ParsingException: If parsing fails.
        """
        try:
            self.logger.info("Parsing artifact content")

            # Use artifact strategy
            artifact_strategy = self._find_strategy(ArtifactStrategy)
            if not artifact_strategy:
                raise ParsingException("Artifact strategy not found")

            return artifact_strategy.parse(content_data)

        except Exception as e:
            self.logger.error(f"Failed to parse artifact content: {e}")
            raise ParsingException(f"Artifact content parsing failed: {e}")

    def _select_strategies_for_main_content(self, module_types: list[str]) -> list[BaseParsingStrategy]:
        """Select appropriate strategies for main content based on module types.

        Args:
            module_types: List of module type names.

        Returns:
            List of strategies to use.
        """
        selected_strategies = []

        # Map content types to strategies
        strategy_map = {
            ContentType.CHARACTER_DATA.value: CharacterDataStrategy,
            ContentType.CHARACTER_STRATEGY.value: StrategyContentStrategy,
            ContentType.CHARACTER_STRATEGY_OLD.value: StrategyContentStrategy,
        }

        # Find strategies that can handle the module types
        for module_type in module_types:
            strategy_class = strategy_map.get(module_type)
            if strategy_class:
                strategy = self._find_strategy(strategy_class)
                if strategy and strategy not in selected_strategies:
                    selected_strategies.append(strategy)

        # If no specific strategies found, use general strategy
        if not selected_strategies:
            general_strategy = self._find_strategy(StrategyContentStrategy)
            if general_strategy:
                selected_strategies.append(general_strategy)

        self.logger.debug(f"Selected {len(selected_strategies)} strategies for main content")
        return selected_strategies

    def _find_strategy(self, strategy_class: type) -> BaseParsingStrategy | None:
        """Find strategy instance by class.

        Args:
            strategy_class: Class of strategy to find.

        Returns:
            Strategy instance or None if not found.
        """
        for strategy in self.strategies:
            if isinstance(strategy, strategy_class):
                return strategy
        return None

    def _parse_with_strategies(
        self, content_data: dict[str, Any], strategies: list[BaseParsingStrategy]
    ) -> dict[str, Any]:
        """Parse content using multiple strategies and merge results.

        Args:
            content_data: Raw content data.
            strategies: List of strategies to use.

        Returns:
            Merged parsed content.
        """
        if not strategies:
            self.logger.warning("No strategies provided for parsing")
            return {"title": "No Content", "modules": {}}

        title = content_data.get("title", "Content")
        merged_result = {"title": title, "modules": {}}

        for strategy in strategies:
            try:
                result = strategy.parse(content_data)

                # Merge modules from this strategy
                strategy_modules = result.get("modules", {})
                for module_name, module_data in strategy_modules.items():
                    if module_name not in merged_result["modules"]:
                        merged_result["modules"][module_name] = module_data
                    else:
                        # Merge components if module already exists
                        existing_components = merged_result["modules"][module_name].get("components", [])
                        new_components = module_data.get("components", [])

                        # Avoid duplicates by title
                        existing_titles = {comp.get("title", "") for comp in existing_components}
                        for comp in new_components:
                            comp_title = comp.get("title", "")
                            if comp_title not in existing_titles:
                                existing_components.append(comp)
                                existing_titles.add(comp_title)

                        merged_result["modules"][module_name]["components"] = existing_components

            except Exception as e:
                self.logger.warning(f"Strategy {strategy.__class__.__name__} failed: {e}")
                continue

        return merged_result


# Factory functions for dependency injection
def create_strategy_based_parser(html_converter: HTMLToMarkdownConverter | None = None) -> StrategyBasedContentParser:
    """Create strategy-based content parser.

    Args:
        html_converter: Optional HTML converter.

    Returns:
        StrategyBasedContentParser instance.
    """
    return StrategyBasedContentParser(html_converter)


def create_html_converter() -> HTMLToMarkdownConverter:
    """Create HTML converter.

    Returns:
        HTMLToMarkdownConverter instance.
    """
    return HTMLToMarkdownConverter()


# Backward compatibility with original ContentParser
class ContentParser:
    """Legacy ContentParser wrapper for backward compatibility."""

    def __init__(self):
        """Initialize legacy parser."""
        self.strategy_parser = StrategyBasedContentParser()
        self.logger = LoggerMixin().logger

    def parse_main_content(self, content_data: dict[str, Any]) -> dict[str, Any]:
        """Parse main content (legacy interface)."""
        return self.strategy_parser.parse_main_content(content_data)

    def parse_character_profile(self, content_data: dict[str, Any]) -> dict[str, Any]:
        """Parse character profile (legacy interface)."""
        return self.strategy_parser.parse_character_profile(content_data)

    def parse_strategy_content(self, content_data: dict[str, Any]) -> dict[str, Any]:
        """Parse strategy content (legacy interface)."""
        return self.strategy_parser.parse_strategy_content(content_data)

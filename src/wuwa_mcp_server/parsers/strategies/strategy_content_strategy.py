"""Strategy content parsing strategy."""

from typing import Any

from ...domain.value_objects import ContentType
from ..html_converter import HTMLToMarkdownConverter
from .base_strategy import BaseParsingStrategy


class StrategyContentStrategy(BaseParsingStrategy):
    """Strategy for parsing strategy content (角色攻略) without filtering specific types."""

    def __init__(self, html_converter: HTMLToMarkdownConverter | None = None):
        """Initialize strategy.

        Args:
            html_converter: HTML converter instance. Creates one if None.
        """
        super().__init__()
        self.html_converter = html_converter or HTMLToMarkdownConverter()
        # Strategy content processes all modules without type filtering

    def can_handle(self, content_type: str) -> bool:
        """Check if this strategy can handle the content type.

        Strategy content handles all types since it processes everything.
        """
        return True

    def get_supported_content_types(self) -> list[ContentType]:
        """Get supported content types."""
        # Return all strategy-related content types
        return [
            ContentType.CHARACTER_STRATEGY,
            ContentType.CHARACTER_STRATEGY_OLD,
        ]

    def parse(self, content_data: dict[str, Any]) -> dict[str, Any]:
        """Parse strategy content without module filtering.

        Args:
            content_data: Raw content data from API.

        Returns:
            Parsed content structure.
        """
        if not self.validate_content_data(content_data):
            self.logger.error("Invalid content data structure for strategy content")
            return self.create_result_structure("Invalid Data")

        title = self.extract_title(content_data)
        result = self.create_result_structure(title)

        # Process all modules without filtering
        modules_data = content_data.get("modules", [])

        for module in modules_data:
            module_title = module.get("title", "")

            parsed_module = self._parse_strategy_module(module)
            if parsed_module:
                result["modules"][module_title] = parsed_module

        return result

    def _parse_strategy_module(self, module: dict[str, Any]) -> dict[str, Any] | None:
        """Parse a strategy module.

        Args:
            module: Module data.

        Returns:
            Parsed module structure or None if empty.
        """
        module_data = {"components": []}
        components = module.get("components", [])
        processed_titles = set()  # For deduplication

        for component in components:
            component_title = component.get("title", "Component")

            # Skip duplicates
            if component_title in processed_titles:
                continue
            processed_titles.add(component_title)

            parsed_component = self._parse_strategy_component(component, component_title)
            if parsed_component:
                module_data["components"].append(parsed_component)

        return module_data if module_data["components"] else None

    def _parse_strategy_component(self, component: dict[str, Any], component_title: str) -> dict[str, Any] | None:
        """Parse a strategy component.

        Args:
            component: Component data.
            component_title: Component title.

        Returns:
            Parsed component structure or None if empty.
        """
        try:
            component_data = {}

            # Handle tabs
            if component.get("tabs"):
                component_data["tabs"] = []
                for tab in component["tabs"]:
                    tab_title = tab.get("title", "Tab")
                    tab_content = tab.get("content", "")

                    parsed_content = self.html_converter.parse_html_content(tab_content)

                    component_data["tabs"].append({"title": tab_title, "parsed_content": parsed_content})

            # Handle direct content
            elif component.get("content"):
                content = component["content"]
                parsed_content = self.html_converter.parse_html_content(content)
                component_data["parsed_content"] = parsed_content

            if component_data:
                return {"title": component_title, "data": component_data}
            else:
                return None

        except Exception as e:
            self.logger.error(f"Failed to parse strategy component '{component_title}': {e}")
            return None

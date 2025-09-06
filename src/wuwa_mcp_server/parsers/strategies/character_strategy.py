"""Character-specific parsing strategies."""

from typing import Any

from ...domain.value_objects import ContentType
from ..html_converter import HTMLToMarkdownConverter
from .base_strategy import BaseParsingStrategy


class CharacterDataStrategy(BaseParsingStrategy):
    """Strategy for parsing character basic data (基础资料)."""

    def __init__(self, html_converter: HTMLToMarkdownConverter = None):
        """Initialize strategy.

        Args:
            html_converter: HTML converter instance. Creates one if None.
        """
        super().__init__()
        self.html_converter = html_converter or HTMLToMarkdownConverter()
        self.supported_types = [ContentType.CHARACTER_DATA.value]

    def can_handle(self, content_type: str) -> bool:
        """Check if this strategy can handle the content type."""
        return content_type in self.supported_types

    def get_supported_content_types(self) -> list[ContentType]:
        """Get supported content types."""
        return [ContentType.CHARACTER_DATA]

    def parse(self, content_data: dict[str, Any]) -> dict[str, Any]:
        """Parse character data content.

        Args:
            content_data: Raw content data from API.

        Returns:
            Parsed content structure.
        """
        if not self.validate_content_data(content_data):
            self.logger.error("Invalid content data structure for character data")
            return self.create_result_structure("Invalid Data")

        title = self.extract_title(content_data)
        result = self.create_result_structure(title)

        # Filter modules for character data
        modules_data = content_data.get("modules", [])
        target_modules = self.supported_types

        for module in modules_data:
            module_title = module.get("title", "")
            if module_title not in target_modules:
                continue

            parsed_module = self._parse_character_data_module(module)
            if parsed_module:
                result["modules"][module_title] = parsed_module

        return result

    def _parse_character_data_module(self, module: dict[str, Any]) -> dict[str, Any]:
        """Parse a character data module.

        Args:
            module: Module data.

        Returns:
            Parsed module structure.
        """
        module_data = {"components": []}
        components = module.get("components", [])

        for component in components:
            parsed_component = self._parse_character_data_component(component)
            if parsed_component:
                module_data["components"].append(parsed_component)

        return module_data if module_data["components"] else None

    def _parse_character_data_component(self, component: dict[str, Any]) -> dict[str, Any]:
        """Parse a character data component.

        Args:
            component: Component data.

        Returns:
            Parsed component structure.
        """
        try:
            # Extract role data from component
            role_data = self.safe_get_nested(component, ["role"], {})

            if not role_data:
                self.logger.warning("No role data found in character data component")
                return None

            # Extract basic information
            title = role_data.get("title", "Character")
            subtitle = role_data.get("subtitle", "")
            info_list = role_data.get("info", [])

            # Extract info texts
            info_texts = []
            for info_item in info_list:
                text = info_item.get("text", "")
                if text:
                    info_texts.append(text)

            component_data = {
                "title": title,
                "subtitle": subtitle,
                "info_texts": info_texts,
            }

            return {"title": title, "data": component_data}

        except Exception as e:
            self.logger.error(f"Failed to parse character data component: {e}")
            return None


class CharacterProfileStrategy(BaseParsingStrategy):
    """Strategy for parsing character profile data (角色档案)."""

    def __init__(self, html_converter: HTMLToMarkdownConverter = None):
        """Initialize strategy.

        Args:
            html_converter: HTML converter instance. Creates one if None.
        """
        super().__init__()
        self.html_converter = html_converter or HTMLToMarkdownConverter()
        self.supported_types = [ContentType.CHARACTER_PROFILE.value]

    def can_handle(self, content_type: str) -> bool:
        """Check if this strategy can handle the content type."""
        return content_type in self.supported_types

    def get_supported_content_types(self) -> list[ContentType]:
        """Get supported content types."""
        return [ContentType.CHARACTER_PROFILE]

    def parse(self, content_data: dict[str, Any]) -> dict[str, Any]:
        """Parse character profile content.

        Args:
            content_data: Raw content data from API.

        Returns:
            Parsed content structure.
        """
        if not self.validate_content_data(content_data):
            self.logger.error("Invalid content data structure for character profile")
            return self.create_result_structure("Invalid Data")

        title = self.extract_title(content_data)
        result = self.create_result_structure(title)

        # Filter modules for character profile
        modules_data = content_data.get("modules", [])
        target_modules = self.supported_types

        for module in modules_data:
            module_title = module.get("title", "")
            if module_title not in target_modules:
                continue

            parsed_module = self._parse_general_module(module)
            if parsed_module:
                result["modules"][module_title] = parsed_module

        return result

    def _parse_general_module(self, module: dict[str, Any]) -> dict[str, Any]:
        """Parse a general module with components.

        Args:
            module: Module data.

        Returns:
            Parsed module structure.
        """
        module_data = {"components": []}
        components = module.get("components", [])

        for component in components:
            parsed_component = self._parse_general_component(component)
            if parsed_component:
                module_data["components"].append(parsed_component)

        return module_data if module_data["components"] else None

    def _parse_general_component(self, component: dict[str, Any]) -> dict[str, Any]:
        """Parse a general component with tabs or content.

        Args:
            component: Component data.

        Returns:
            Parsed component structure.
        """
        try:
            component_title = component.get("title", "Component")
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

            return {"title": component_title, "data": component_data} if component_data else None

        except Exception as e:
            self.logger.error(f"Failed to parse general component: {e}")
            return None


class CharacterDevelopmentStrategy(BaseParsingStrategy):
    """Strategy for parsing character development data (角色养成)."""

    def __init__(self, html_converter: HTMLToMarkdownConverter = None):
        """Initialize strategy.

        Args:
            html_converter: HTML converter instance. Creates one if None.
        """
        super().__init__()
        self.html_converter = html_converter or HTMLToMarkdownConverter()
        self.supported_types = [ContentType.CHARACTER_DEVELOPMENT.value]

    def can_handle(self, content_type: str) -> bool:
        """Check if this strategy can handle the content type."""
        return content_type in self.supported_types

    def get_supported_content_types(self) -> list[ContentType]:
        """Get supported content types."""
        return [ContentType.CHARACTER_DEVELOPMENT]

    def parse(self, content_data: dict[str, Any]) -> dict[str, Any]:
        """Parse character development content.

        Args:
            content_data: Raw content data from API.

        Returns:
            Parsed content structure.
        """
        if not self.validate_content_data(content_data):
            self.logger.error("Invalid content data structure for character development")
            return self.create_result_structure("Invalid Data")

        title = self.extract_title(content_data)
        result = self.create_result_structure(title)

        # Filter modules for character development
        modules_data = content_data.get("modules", [])
        target_modules = self.supported_types

        for module in modules_data:
            module_title = module.get("title", "")
            if module_title not in target_modules:
                continue

            parsed_module = self._parse_development_module(module)
            if parsed_module:
                result["modules"][module_title] = parsed_module

        return result

    def _parse_development_module(self, module: dict[str, Any]) -> dict[str, Any]:
        """Parse a character development module.

        Args:
            module: Module data.

        Returns:
            Parsed module structure.
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

            parsed_component = self._parse_development_component(component, component_title)
            if parsed_component:
                module_data["components"].append(parsed_component)

        return module_data if module_data["components"] else None

    def _parse_development_component(self, component: dict[str, Any], component_title: str) -> dict[str, Any]:
        """Parse a development component with special handling for resonance chain.

        Args:
            component: Component data.
            component_title: Component title.

        Returns:
            Parsed component structure.
        """
        try:
            component_data = {}

            # Handle tabs (like skill introduction)
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

                # Special handling for resonance chain (共鸣链)
                if component_title == "共鸣链":
                    # Prioritize tables for resonance chain
                    if parsed_content.get("tables"):
                        component_data["parsed_content"] = {"markdown_content": "", "tables": parsed_content["tables"]}
                    else:
                        component_data["parsed_content"] = parsed_content
                else:
                    component_data["parsed_content"] = parsed_content

            return {"title": component_title, "data": component_data} if component_data else None

        except Exception as e:
            self.logger.error(f"Failed to parse development component '{component_title}': {e}")
            return None

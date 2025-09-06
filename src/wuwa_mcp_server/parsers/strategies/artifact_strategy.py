"""Artifact parsing strategy."""

from typing import Any

from ...domain.value_objects import ContentType
from ..html_converter import HTMLToMarkdownConverter
from .base_strategy import BaseParsingStrategy


class ArtifactStrategy(BaseParsingStrategy):
    """Strategy for parsing artifact (声骸) content."""

    def __init__(self, html_converter: HTMLToMarkdownConverter = None):
        """Initialize strategy.

        Args:
            html_converter: HTML converter instance. Creates one if None.
        """
        super().__init__()
        self.html_converter = html_converter or HTMLToMarkdownConverter()
        # Artifacts don't have a specific content type enum value,
        # so we'll handle all modules for artifact data

    def can_handle(self, content_type: str) -> bool:
        """Check if this strategy can handle the content type.

        For artifacts, we handle all modules since there isn't a specific
        artifact content type defined in the enum.
        """
        # For artifacts, we accept any content type and parse all modules
        return True

    def get_supported_content_types(self) -> list[ContentType]:
        """Get supported content types."""
        # Return empty list since we handle all modules for artifacts
        return []

    def parse(self, content_data: dict[str, Any]) -> dict[str, Any]:
        """Parse artifact content.

        Args:
            content_data: Raw content data from API.

        Returns:
            Parsed content structure.
        """
        if not self.validate_content_data(content_data):
            self.logger.error("Invalid content data structure for artifact")
            return self.create_result_structure("Invalid Data")

        title = self.extract_title(content_data)
        result = self.create_result_structure(title)

        # Parse all modules for artifacts
        modules_data = content_data.get("modules", [])

        for module in modules_data:
            module_title = module.get("title", "")

            parsed_module = self._parse_artifact_module(module)
            if parsed_module:
                result["modules"][module_title] = parsed_module

        return result

    def _parse_artifact_module(self, module: dict[str, Any]) -> dict[str, Any]:
        """Parse an artifact module.

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

            parsed_component = self._parse_artifact_component(component, component_title)
            if parsed_component:
                module_data["components"].append(parsed_component)

        return module_data if module_data["components"] else None

    def _parse_artifact_component(self, component: dict[str, Any], component_title: str) -> dict[str, Any]:
        """Parse an artifact component.

        Args:
            component: Component data.
            component_title: Component title.

        Returns:
            Parsed component structure.
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

            return {"title": component_title, "data": component_data} if component_data else None

        except Exception as e:
            self.logger.error(f"Failed to parse artifact component '{component_title}': {e}")
            return None

    def extract_set_effects(self, component_data: dict[str, Any]) -> list[dict[str, str]]:
        """Extract artifact set effects from component data.

        Args:
            component_data: Component data containing set effects.

        Returns:
            List of set effects with piece count and description.
        """
        set_effects = []

        # This would need to be implemented based on the actual structure
        # of artifact data. For now, return empty list.
        # In a real implementation, we would:
        # 1. Look for tables containing set effect information
        # 2. Parse the table rows for piece counts and effects
        # 3. Extract echo type information

        try:
            parsed_content = component_data.get("parsed_content", {})
            tables = parsed_content.get("tables", [])

            # Look for tables that contain set effect information
            for table in tables:
                if len(table) >= 2:  # Has header and at least one data row
                    headers = table[0]

                    # Check if this looks like a set effect table
                    if any("effect" in header.lower() or "效果" in header for header in headers):
                        for row in table[1:]:
                            if len(row) >= 2:
                                # Try to extract piece count and effect
                                piece_info = row[0]
                                effect_desc = row[1]

                                set_effects.append({"piece_info": piece_info, "effect_description": effect_desc})

        except Exception as e:
            self.logger.warning(f"Failed to extract set effects: {e}")

        return set_effects

    def extract_echo_types(self, parsed_data: dict[str, Any]) -> list[str]:
        """Extract echo types from parsed artifact data.

        Args:
            parsed_data: Full parsed artifact data.

        Returns:
            List of echo type names.
        """
        echo_types = []

        try:
            modules = parsed_data.get("modules", {})

            # Look through all modules for echo information
            for module_name, module_data in modules.items():
                components = module_data.get("components", [])

                for component in components:
                    # Look for components that might contain echo information
                    component_title = component.get("title", "")
                    if "声骸" in component_title or "echo" in component_title.lower():
                        data = component.get("data", {})
                        parsed_content = data.get("parsed_content", {})
                        tables = parsed_content.get("tables", [])

                        # Extract echo names from tables
                        for table in tables:
                            if len(table) >= 2:
                                # Skip header row, process data rows
                                for row in table[1:]:
                                    for cell in row:
                                        # Simple heuristic: if cell contains text that looks like echo name
                                        if cell and len(cell.strip()) > 2 and len(cell.strip()) < 20:
                                            echo_types.append(cell.strip())

        except Exception as e:
            self.logger.warning(f"Failed to extract echo types: {e}")

        # Remove duplicates and return
        return list(set(echo_types))

"""Markdown builder using Builder pattern for flexible document construction."""

from typing import Any

from ..core.exceptions import MarkdownGenerationException
from ..core.logging_config import LoggerMixin
from ..domain.entities import MarkdownDocument
from ..domain.value_objects import MarkdownSection
from ..domain.value_objects import TableData
from .markdown_formatter import MarkdownFormatter


class MarkdownBuilder(LoggerMixin):
    """Builder for constructing markdown documents using fluent interface."""

    def __init__(self):
        """Initialize the builder."""
        self.formatter = MarkdownFormatter()
        self.reset()

    def reset(self) -> "MarkdownBuilder":
        """Reset the builder to initial state."""
        self.document = MarkdownDocument(title="")
        self.current_content: list[str] = []
        return self

    def set_title(self, title: str) -> "MarkdownBuilder":
        """Set document title."""
        if not title:
            raise MarkdownGenerationException("Document title cannot be empty")

        self.document.title = title
        return self

    def add_header(self, text: str, level: int = 1) -> "MarkdownBuilder":
        """Add a header to the current content."""
        if not text:
            self.logger.warning("Attempting to add empty header")
            return self

        try:
            formatted_header = self.formatter.header_level(level).format(text)
            self.current_content.append(formatted_header)
            self.current_content.append("")  # Add blank line after header
        except ValueError as e:
            raise MarkdownGenerationException(f"Invalid header level: {e}")

        return self

    def add_text(self, text: str) -> "MarkdownBuilder":
        """Add formatted text to the current content."""
        if not text:
            return self

        formatted_text = self.formatter.text.format(text)
        if formatted_text:
            self.current_content.append(formatted_text)

        return self

    def add_paragraph(self, text: str) -> "MarkdownBuilder":
        """Add a paragraph with blank line separation."""
        self.add_text(text)
        self.current_content.append("")  # Add blank line
        return self

    def add_bold_text(self, text: str) -> "MarkdownBuilder":
        """Add bold text to the current content."""
        if not text:
            return self

        formatted = self.formatter.emphasis.format_bold(text)
        self.current_content.append(formatted)
        return self

    def add_italic_text(self, text: str) -> "MarkdownBuilder":
        """Add italic text to the current content."""
        if not text:
            return self

        formatted = self.formatter.emphasis.format(text)
        self.current_content.append(formatted)
        return self

    def add_unordered_list(self, items: list[str]) -> "MarkdownBuilder":
        """Add an unordered list."""
        if not items:
            return self

        formatted_list = self.formatter.unordered_list().format(items)
        if formatted_list:
            self.current_content.append(formatted_list)
            self.current_content.append("")  # Add blank line

        return self

    def add_ordered_list(self, items: list[str]) -> "MarkdownBuilder":
        """Add an ordered list."""
        if not items:
            return self

        formatted_list = self.formatter.ordered_list().format(items)
        if formatted_list:
            self.current_content.append(formatted_list)
            self.current_content.append("")  # Add blank line

        return self

    def add_table(self, table_data: TableData) -> "MarkdownBuilder":
        """Add a table using TableData."""
        try:
            formatted_table = self.formatter.table.format_from_table_data(table_data)
            if formatted_table:
                self.current_content.append(formatted_table)
                self.current_content.append("")  # Add blank line
        except Exception as e:
            self.logger.error(f"Failed to format table: {e}")
            raise MarkdownGenerationException(f"Table formatting failed: {e}")

        return self

    def add_table_from_arrays(self, headers: list[str], rows: list[list[str]]) -> "MarkdownBuilder":
        """Add a table from header and row arrays."""
        if not headers:
            self.logger.warning("Cannot add table without headers")
            return self

        try:
            table_data = TableData(headers=headers, rows=rows)
            return self.add_table(table_data)
        except ValueError as e:
            self.logger.error(f"Invalid table data: {e}")
            raise MarkdownGenerationException(f"Invalid table data: {e}")

    def add_link(self, text: str, url: str) -> "MarkdownBuilder":
        """Add a markdown link."""
        if not text or not url:
            self.logger.warning("Skipping link with missing text or URL")
            return self

        formatted_link = self.formatter.link.format(text, url)
        self.current_content.append(formatted_link)
        return self

    def add_horizontal_rule(self) -> "MarkdownBuilder":
        """Add a horizontal rule."""
        hr = self.formatter.hr.format()
        self.current_content.append("")  # Blank line before
        self.current_content.append(hr)
        self.current_content.append("")  # Blank line after
        return self

    def add_raw_content(self, content: str) -> "MarkdownBuilder":
        """Add raw markdown content without formatting."""
        if content:
            self.current_content.append(content)
        return self

    def start_section(self, title: str, level: int = 2) -> "MarkdownBuilder":
        """Start a new section and save current content."""
        # Save current section if it has content
        self._save_current_section()

        # Start new section
        self.add_header(title, level)
        return self

    def build(self) -> MarkdownDocument:
        """Build and return the final markdown document."""
        # Save any remaining current content
        self._save_current_section()

        if not self.document.title:
            raise MarkdownGenerationException("Document must have a title")

        return self.document

    def build_as_string(self) -> str:
        """Build and return as markdown string."""
        document = self.build()
        return document.to_markdown()

    def _save_current_section(self) -> None:
        """Save current content as a section."""
        if not self.current_content:
            return

        # Find the first header in current content to use as section title
        section_title = "Content"
        section_level = 2
        content_lines = []

        for i, line in enumerate(self.current_content):
            if line.startswith("#"):
                # Extract header info
                header_match = line.split(None, 1)
                if len(header_match) >= 2:
                    section_level = len(header_match[0])  # Count #'s
                    section_title = header_match[1]
                # Skip the header line and next empty line
                content_lines = self.current_content[i + 1 :]
                if content_lines and content_lines[0] == "":
                    content_lines = content_lines[1:]
                break
        else:
            content_lines = self.current_content

        # Create section with remaining content
        content = "\n".join(content_lines).strip()
        if content or section_title != "Content":  # Always save if we found a header
            section = MarkdownSection(title=section_title, level=section_level, content=content)
            self.document.add_section(section)

        # Reset current content
        self.current_content = []


class LegacyMarkdownConverter(LoggerMixin):
    """Converter for legacy parsed data structure to new builder system."""

    def __init__(self):
        """Initialize the converter."""
        self.builder = MarkdownBuilder()

    def convert(self, parsed_data: dict[str, Any]) -> str:
        """Convert legacy parsed data to markdown using the new builder."""
        try:
            # Reset builder and set title
            title = parsed_data.get("title", "Unnamed Document")
            self.builder.reset().set_title(title)

            # Process modules
            modules = parsed_data.get("modules", {})
            for module_title, module_data in modules.items():
                self._process_module(module_title, module_data)

            # Add strategy link if present
            strategy_item_id = parsed_data.get("strategy_item_id")
            if strategy_item_id:
                self._add_strategy_link(strategy_item_id)

            return self.builder.build_as_string()

        except Exception as e:
            self.logger.error(f"Failed to convert legacy data: {e}")
            raise MarkdownGenerationException(f"Legacy conversion failed: {e}")

    def _process_module(self, module_title: str, module_data: dict[str, Any]) -> None:
        """Process a single module."""
        self.builder.start_section(module_title)

        components = module_data.get("components", [])
        processed_titles = set()  # For deduplication

        for component in components:
            comp_title = component.get("title", "Unnamed Component")
            if comp_title in processed_titles:
                continue
            processed_titles.add(comp_title)

            self._process_component(component, comp_title, module_title)

    def _process_component(self, component: dict[str, Any], comp_title: str, module_title: str) -> None:
        """Process a single component."""
        data = component.get("data", {})

        # Handle CHARACTER_DATA specific structure
        if self._is_character_data(data):
            self._process_character_data(data, comp_title)
        # Handle tabs (skill introduction)
        elif "tabs" in data:
            self._process_tabs(data, comp_title)
        # Handle other components
        elif "parsed_content" in data:
            self._process_parsed_content(data, comp_title, module_title)

    def _is_character_data(self, data: dict[str, Any]) -> bool:
        """Check if this is character data structure."""
        return "subtitle" in data and "info_texts" in data

    def _process_character_data(self, data: dict[str, Any], comp_title: str) -> None:
        """Process character data structure."""
        self.builder.start_section(comp_title, level=3)

        subtitle = data.get("subtitle", "")
        if subtitle:
            self.builder.add_text(f"- name: **{subtitle}**").add_text("")

        info_texts = data.get("info_texts", [])
        if info_texts:
            for text in info_texts:
                self.builder.add_text(f"- {text}")
            self.builder.add_text("")

    def _process_tabs(self, data: dict[str, Any], comp_title: str) -> None:
        """Process component with tabs."""
        self.builder.start_section(comp_title, level=3)

        for tab in data["tabs"]:
            tab_title = tab.get("title", "Unnamed Tab")
            self.builder.add_header(tab_title, level=4)

            parsed_content = tab.get("parsed_content", {})
            self._add_parsed_content(parsed_content)

    def _process_parsed_content(self, data: dict[str, Any], comp_title: str, module_title: str) -> None:
        """Process component with parsed_content."""
        self.builder.start_section(comp_title, level=3)

        parsed_content = data["parsed_content"]

        # Special handling for "共鸣链" (Resonance Chain)
        if comp_title == "共鸣链":
            tables = parsed_content.get("tables", [])
            if tables:
                for table in tables:
                    if table and len(table) > 1:  # Has headers and data
                        self.builder.add_table_from_arrays(table[0], table[1:])
                return

        # Normal processing
        self._add_parsed_content(parsed_content)

    def _add_parsed_content(self, parsed_content: dict[str, Any]) -> None:
        """Add parsed content to builder."""
        # Add markdown content
        markdown_content = parsed_content.get("markdown_content", "")
        if markdown_content:
            self.builder.add_raw_content(markdown_content)
        else:
            self.builder.add_text("*(No Content)*")

        self.builder.add_text("")

        # Add tables
        tables = parsed_content.get("tables", [])
        for table in tables:
            if table and len(table) > 1:  # Has headers and data
                self.builder.add_table_from_arrays(table[0], table[1:])

    def _add_strategy_link(self, strategy_item_id: str) -> None:
        """Add strategy link section."""
        self.builder.start_section("Character Strategy Link")
        self.builder.add_text(f"- Strategy Item ID: {strategy_item_id}")
        url = f"https://wiki.kurobbs.com/mc/item/{strategy_item_id}"
        self.builder.add_link("View Strategy", url)

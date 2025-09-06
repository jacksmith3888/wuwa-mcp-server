"""HTML to Markdown converter with improved architecture."""

import re
from typing import Any

from bs4 import BeautifulSoup
from bs4 import NavigableString

from ..core.exceptions import HTMLParsingException
from ..core.interfaces import BaseHTMLConverter
from ..core.logging_config import LoggerMixin


class HTMLToMarkdownConverter(BaseHTMLConverter, LoggerMixin):
    """Converts HTML content to Markdown using BeautifulSoup."""

    def __init__(self):
        """Initialize the converter."""
        pass

    def convert(self, html_content: str) -> str:
        """Convert HTML content to markdown.

        Args:
            html_content: HTML string to convert.

        Returns:
            Markdown string.

        Raises:
            HTMLParsingException: If HTML parsing fails.
        """
        if not html_content:
            return ""

        try:
            soup = BeautifulSoup(html_content, "html.parser")
            markdown = "".join(self._convert_tag_to_markdown(child) for child in soup.children)
            return markdown.strip()

        except Exception as e:
            self.logger.error(f"HTML parsing failed: {e}")
            raise HTMLParsingException(
                f"Failed to convert HTML to markdown: {e}",
                html_content=html_content[:500],  # Only log first 500 chars
            )

    def extract_tables(self, html_content: str) -> list[list[list[str]]]:
        """Extract tables from HTML content.

        Args:
            html_content: HTML string to extract tables from.

        Returns:
            List of tables, where each table is a list of rows,
            and each row is a list of cell contents.

        Raises:
            HTMLParsingException: If HTML parsing fails.
        """
        if not html_content:
            return []

        try:
            soup = BeautifulSoup(html_content, "html.parser")
            tables = []

            for table_tag in soup.find_all("table"):
                table_data = self._extract_table_data(table_tag)
                if table_data:
                    tables.append(table_data)

            return tables

        except Exception as e:
            self.logger.error(f"Table extraction failed: {e}")
            raise HTMLParsingException(f"Failed to extract tables from HTML: {e}", html_content=html_content[:500])

    def parse_html_content(self, html_content: str) -> dict[str, Any]:
        """Parse HTML content and return both markdown and table data.

        Args:
            html_content: HTML string to parse.

        Returns:
            Dictionary with 'markdown_content' and 'tables' keys.
        """
        if not html_content:
            return {"markdown_content": "", "tables": []}

        try:
            markdown_content = self.convert(html_content)
            tables = self.extract_tables(html_content)

            return {"markdown_content": markdown_content, "tables": tables}

        except HTMLParsingException:
            raise
        except Exception as e:
            self.logger.error(f"HTML content parsing failed: {e}")
            return {"markdown_content": f"<error>Failed to parse HTML: {e!s}</error>", "tables": []}

    def _convert_tag_to_markdown(self, tag: Any) -> str:
        """Convert a BeautifulSoup tag to markdown recursively.

        Args:
            tag: BeautifulSoup tag or NavigableString.

        Returns:
            Markdown representation of the tag.
        """
        if isinstance(tag, NavigableString):
            return str(tag).strip()

        if not hasattr(tag, "name"):
            return ""

        # Dispatch to specific handlers
        handler_map = {
            "p": self._handle_paragraph,
            "strong": self._handle_strong,
            "b": self._handle_strong,  # Alias for strong
            "em": self._handle_emphasis,
            "i": self._handle_emphasis,  # Alias for em
            "hr": self._handle_horizontal_rule,
            "br": self._handle_line_break,
            "table": self._handle_table,
            "span": self._handle_span,
            "div": self._handle_div,
            "h1": lambda tag: self._handle_header(tag, 1),
            "h2": lambda tag: self._handle_header(tag, 2),
            "h3": lambda tag: self._handle_header(tag, 3),
            "h4": lambda tag: self._handle_header(tag, 4),
            "h5": lambda tag: self._handle_header(tag, 5),
            "h6": lambda tag: self._handle_header(tag, 6),
            "ul": self._handle_unordered_list,
            "ol": self._handle_ordered_list,
        }

        handler = handler_map.get(tag.name)
        if handler:
            return handler(tag)
        else:
            # Default: process children
            return self._process_children(tag)

    def _handle_paragraph(self, tag) -> str:
        """Handle <p> tags."""
        content = self._process_children(tag).strip()
        return f"{content}\n\n" if content else ""

    def _handle_strong(self, tag) -> str:
        """Handle <strong> and <b> tags."""
        content = self._process_children(tag).strip()
        return f"**{content}**" if content else ""

    def _handle_emphasis(self, tag) -> str:
        """Handle <em> and <i> tags."""
        content = self._process_children(tag).strip()
        return f"*{content}*" if content else ""

    def _handle_horizontal_rule(self, tag) -> str:
        """Handle <hr> tags."""
        return "---\n\n"

    def _handle_line_break(self, tag) -> str:
        """Handle <br> tags."""
        return "\n"

    def _handle_table(self, tag) -> str:
        """Handle <table> tags."""
        return self._convert_table_to_markdown(tag) + "\n\n"

    def _handle_span(self, tag) -> str:
        """Handle <span> tags."""
        return self._process_children(tag)

    def _handle_div(self, tag) -> str:
        """Handle <div> tags."""
        return self._process_children(tag)

    def _handle_header(self, tag, level: int) -> str:
        """Handle header tags (h1-h6)."""
        content = self._process_children(tag).strip()
        if content:
            prefix = "#" * level
            return f"{prefix} {content}\n\n"
        return ""

    def _handle_unordered_list(self, tag) -> str:
        """Handle <ul> tags."""
        items = []
        for item in tag.find_all("li", recursive=False):
            item_content = self._process_children(item).strip()
            if item_content:
                items.append(f"* {item_content}")
        return "\n".join(items) + "\n\n" if items else ""

    def _handle_ordered_list(self, tag) -> str:
        """Handle <ol> tags."""
        items = []
        for i, item in enumerate(tag.find_all("li", recursive=False), 1):
            item_content = self._process_children(item).strip()
            if item_content:
                items.append(f"{i}. {item_content}")
        return "\n".join(items) + "\n\n" if items else ""

    def _process_children(self, tag) -> str:
        """Process all children of a tag."""
        return "".join(self._convert_tag_to_markdown(child) for child in tag.children)

    def _convert_table_to_markdown(self, table_tag) -> str:
        """Convert table tag to markdown table format."""
        rows = table_tag.find_all("tr")
        if not rows:
            return ""

        lines = []

        # Process header row
        header_cells = rows[0].find_all(["th", "td"])
        if header_cells:
            header_texts = [self._clean_cell_content(cell) for cell in header_cells]
            lines.append("| " + " | ".join(header_texts) + " |")
            lines.append("| " + " | ".join(["---"] * len(header_cells)) + " |")

        # Process data rows
        for row in rows[1:]:
            data_cells = row.find_all("td")
            if data_cells and len(data_cells) == len(header_cells):
                row_texts = [self._clean_cell_content(cell) for cell in data_cells]
                lines.append("| " + " | ".join(row_texts) + " |")

        return "\n".join(lines)

    def _extract_table_data(self, table_tag) -> list[list[str]]:
        """Extract table data as list of lists."""
        rows = table_tag.find_all("tr")
        if not rows:
            return []

        table_data = []

        for row in rows:
            cells = row.find_all(["th", "td"])
            if cells:
                row_data = [self._clean_cell_content(cell) for cell in cells]
                table_data.append(row_data)

        return table_data

    def _clean_cell_content(self, cell) -> str:
        """Clean cell content for table formatting."""
        if not cell:
            return ""

        # Get text and clean whitespace
        text = " ".join(cell.get_text(strip=True).split())

        # Escape pipe characters for markdown tables
        text = text.replace("|", "\\|")

        return text

    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text content.

        Args:
            text: Text to clean.

        Returns:
            Cleaned text.
        """
        if not text:
            return ""

        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text.strip())

        # Remove unwanted characters
        text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", text)

        return text

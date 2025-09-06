"""Markdown formatting components following SRP and OCP principles."""

from abc import ABC
from abc import abstractmethod

from ..core.logging_config import LoggerMixin
from ..domain.value_objects import TableData


class BaseFormatter(ABC, LoggerMixin):
    """Abstract base class for markdown formatters."""

    @abstractmethod
    def format(self, content: str) -> str:
        """Format content and return markdown string."""
        pass


class TextFormatter(BaseFormatter):
    """Formatter for text content."""

    def format(self, content: str) -> str:
        """Format plain text content."""
        if not content:
            return ""

        # Clean up whitespace
        cleaned = " ".join(content.split())
        return cleaned


class HeaderFormatter(BaseFormatter):
    """Formatter for headers."""

    def __init__(self, level: int = 1):
        """Initialize with header level (1-6)."""
        if not 1 <= level <= 6:
            raise ValueError("Header level must be between 1 and 6")
        self.level = level

    def format(self, content: str) -> str:
        """Format as markdown header."""
        if not content:
            return ""

        prefix = "#" * self.level
        return f"{prefix} {content.strip()}"


class ListFormatter(BaseFormatter):
    """Formatter for lists."""

    def __init__(self, ordered: bool = False):
        """Initialize list formatter.

        Args:
            ordered: If True, create ordered list. Otherwise unordered.
        """
        self.ordered = ordered

    def format(self, items: list[str] | str) -> str:
        """Format items as markdown list."""
        if isinstance(items, str):
            items = [items]

        if not items:
            return ""

        formatted_items = []
        for i, item in enumerate(items, 1):
            if not item.strip():
                continue

            if self.ordered:
                formatted_items.append(f"{i}. {item.strip()}")
            else:
                formatted_items.append(f"- {item.strip()}")

        return "\n".join(formatted_items)


class LinkFormatter(BaseFormatter):
    """Formatter for links."""

    def format(self, text: str, url: str) -> str:
        """Format as markdown link."""
        if not text or not url:
            return text or ""

        return f"[{text}]({url})"

    def format_reference_link(self, text: str, ref_id: str) -> str:
        """Format as reference-style link."""
        if not text or not ref_id:
            return text or ""

        return f"[{text}][{ref_id}]"


class EmphasisFormatter(BaseFormatter):
    """Formatter for text emphasis."""

    def format(self, content: str) -> str:
        """Format with italic emphasis."""
        if not content:
            return ""
        return f"*{content.strip()}*"

    def format_bold(self, content: str) -> str:
        """Format with bold emphasis."""
        if not content:
            return ""
        return f"**{content.strip()}**"

    def format_code(self, content: str) -> str:
        """Format as inline code."""
        if not content:
            return ""
        return f"`{content.strip()}`"


class TableFormatter(BaseFormatter):
    """Formatter for tables following markdown syntax."""

    def format_from_table_data(self, table_data: TableData) -> str:
        """Format TableData as markdown table."""
        return self._format_table(table_data.headers, table_data.rows)

    def format(self, headers: list[str], rows: list[list[str]]) -> str:
        """Format headers and rows as markdown table."""
        return self._format_table(headers, rows)

    def _format_table(self, headers: list[str], rows: list[list[str]]) -> str:
        """Internal method to format table."""
        if not headers:
            self.logger.warning("Cannot create table without headers")
            return ""

        lines = []

        # Format header row
        header_row = "| " + " | ".join(self._clean_cell(h) for h in headers) + " |"
        lines.append(header_row)

        # Format separator row
        separator = "| " + " | ".join(["---"] * len(headers)) + " |"
        lines.append(separator)

        # Format data rows
        for row in rows:
            if len(row) != len(headers):
                self.logger.warning(f"Row has {len(row)} columns, expected {len(headers)}. Skipping row.")
                continue

            row_formatted = "| " + " | ".join(self._clean_cell(cell) for cell in row) + " |"
            lines.append(row_formatted)

        return "\n".join(lines)

    def _clean_cell(self, cell: str) -> str:
        """Clean cell content for table formatting."""
        if not cell:
            return ""

        # Remove line breaks and extra whitespace
        cleaned = " ".join(cell.strip().split())

        # Escape pipe characters
        cleaned = cleaned.replace("|", "\\|")

        return cleaned


class HorizontalRuleFormatter(BaseFormatter):
    """Formatter for horizontal rules."""

    def format(self, content: str = "") -> str:
        """Format as markdown horizontal rule."""
        return "---"


class BlockQuoteFormatter(BaseFormatter):
    """Formatter for block quotes."""

    def format(self, content: str) -> str:
        """Format as markdown blockquote."""
        if not content:
            return ""

        lines = content.strip().split("\n")
        quoted_lines = [f"> {line}" for line in lines]
        return "\n".join(quoted_lines)


class MarkdownFormatter(LoggerMixin):
    """Main markdown formatter that composes various formatters."""

    def __init__(self):
        """Initialize with sub-formatters."""
        self.text = TextFormatter()
        self.header = HeaderFormatter
        self.list = ListFormatter
        self.link = LinkFormatter()
        self.emphasis = EmphasisFormatter()
        self.table = TableFormatter()
        self.hr = HorizontalRuleFormatter()
        self.blockquote = BlockQuoteFormatter()

    def header_level(self, level: int) -> HeaderFormatter:
        """Get header formatter for specific level."""
        return HeaderFormatter(level)

    def ordered_list(self) -> ListFormatter:
        """Get ordered list formatter."""
        return ListFormatter(ordered=True)

    def unordered_list(self) -> ListFormatter:
        """Get unordered list formatter."""
        return ListFormatter(ordered=False)

    def escape_special_chars(self, text: str) -> str:
        """Escape markdown special characters."""
        if not text:
            return ""

        special_chars = {
            "\\": r"\\",
            "`": r"\`",
            "*": r"\*",
            "_": r"\_",
            "{": r"\{",
            "}": r"\}",
            "[": r"\[",
            "]": r"\]",
            "(": r"\(",
            ")": r"\)",
            "#": r"\#",
            "+": r"\+",
            "-": r"\-",
            ".": r"\.",
            "!": r"\!",
        }

        for char, escaped in special_chars.items():
            text = text.replace(char, escaped)

        return text

    def clean_whitespace(self, text: str) -> str:
        """Clean up whitespace in text."""
        if not text:
            return ""

        # Replace multiple whitespace with single space
        cleaned = " ".join(text.split())

        # Remove trailing whitespace from lines
        lines = cleaned.split("\n")
        cleaned_lines = [line.rstrip() for line in lines]

        return "\n".join(cleaned_lines)

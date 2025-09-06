"""Value objects for the WuWa MCP Server domain."""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class ContentType(Enum):
    """Enumeration of content types."""

    CHARACTER_DATA = "基础资料"
    CHARACTER_DEVELOPMENT = "角色养成"
    CHARACTER_STRATEGY = "角色攻略"
    CHARACTER_STRATEGY_OLD = "角色养成推荐"
    CHARACTER_PROFILE = "角色档案"
    ARTIFACT_DATA = "声骸数据"


@dataclass(frozen=True)
class CharacterId:
    """Value object for character identification."""

    entry_id: str
    name: str

    def __post_init__(self):
        if not self.entry_id:
            raise ValueError("Entry ID cannot be empty")
        if not self.name:
            raise ValueError("Name cannot be empty")


@dataclass(frozen=True)
class ArtifactId:
    """Value object for artifact identification."""

    entry_id: str
    name: str

    def __post_init__(self):
        if not self.entry_id:
            raise ValueError("Entry ID cannot be empty")
        if not self.name:
            raise ValueError("Name cannot be empty")


@dataclass(frozen=True)
class TableData:
    """Value object for table data."""

    headers: list[str]
    rows: list[list[str]]

    def __post_init__(self):
        if not self.headers:
            raise ValueError("Table must have headers")

        # Validate all rows have same column count as headers
        header_count = len(self.headers)
        for i, row in enumerate(self.rows):
            if len(row) != header_count:
                raise ValueError(f"Row {i} has {len(row)} columns, expected {header_count}")


@dataclass(frozen=True)
class ComponentData:
    """Value object for component data."""

    title: str
    markdown_content: str
    tables: list[TableData]

    def __post_init__(self):
        if not self.title:
            raise ValueError("Component title cannot be empty")


@dataclass(frozen=True)
class ModuleData:
    """Value object for module data."""

    title: str
    content_type: ContentType
    components: list[ComponentData]

    def __post_init__(self):
        if not self.title:
            raise ValueError("Module title cannot be empty")


@dataclass(frozen=True)
class SkillInfo:
    """Value object for character skill information."""

    name: str
    description: str
    level_data: TableData | None = None

    def __post_init__(self):
        if not self.name:
            raise ValueError("Skill name cannot be empty")


@dataclass(frozen=True)
class CharacterBasicInfo:
    """Value object for character basic information."""

    name: str
    gender: str
    birthplace: str
    weapon: str
    attribute: str

    def __post_init__(self):
        if not self.name:
            raise ValueError("Character name cannot be empty")


@dataclass(frozen=True)
class ArtifactSetEffect:
    """Value object for artifact set effect."""

    piece_count: int
    effect_description: str

    def __post_init__(self):
        if self.piece_count <= 0:
            raise ValueError("Piece count must be positive")
        if not self.effect_description:
            raise ValueError("Effect description cannot be empty")


@dataclass(frozen=True)
class MarkdownSection:
    """Value object for markdown section."""

    title: str
    level: int  # Header level (1-6)
    content: str

    def __post_init__(self):
        if not self.title:
            raise ValueError("Section title cannot be empty")
        if self.level < 1 or self.level > 6:
            raise ValueError("Header level must be between 1 and 6")


@dataclass(frozen=True)
class APIResponse:
    """Value object for API response."""

    success: bool
    data: dict[str, Any] | None
    error_message: str | None = None
    status_code: int | None = None

    def __post_init__(self):
        if not self.success and not self.error_message:
            raise ValueError("Failed response must have error message")


@dataclass(frozen=True)
class ParsedContent:
    """Value object for parsed content."""

    title: str
    modules: list[ModuleData]
    strategy_item_id: str | None = None

    def __post_init__(self):
        if not self.title:
            raise ValueError("Parsed content title cannot be empty")

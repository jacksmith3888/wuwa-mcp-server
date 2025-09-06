"""Domain entities for WuWa MCP Server."""

from dataclasses import dataclass
from dataclasses import field

from .value_objects import ArtifactId
from .value_objects import ArtifactSetEffect
from .value_objects import CharacterBasicInfo
from .value_objects import CharacterId
from .value_objects import ComponentData
from .value_objects import ContentType
from .value_objects import MarkdownSection
from .value_objects import SkillInfo


@dataclass
class ContentModule:
    """Entity representing a content module."""

    title: str
    content_type: ContentType
    components: list[ComponentData] = field(default_factory=list)

    def add_component(self, component: ComponentData) -> None:
        """Add a component to this module."""
        self.components.append(component)

    def get_component_by_title(self, title: str) -> ComponentData | None:
        """Get component by title."""
        return next((comp for comp in self.components if comp.title == title), None)


@dataclass
class Character:
    """Entity representing a character."""

    id: CharacterId
    basic_info: CharacterBasicInfo | None = None
    modules: list[ContentModule] = field(default_factory=list)
    skills: list[SkillInfo] = field(default_factory=list)
    strategy_item_id: str | None = None

    def add_module(self, module: ContentModule) -> None:
        """Add a module to this character."""
        self.modules.append(module)

    def get_module_by_type(self, content_type: ContentType) -> ContentModule | None:
        """Get module by content type."""
        return next((mod for mod in self.modules if mod.content_type == content_type), None)

    def add_skill(self, skill: SkillInfo) -> None:
        """Add a skill to this character."""
        self.skills.append(skill)

    def get_skill_by_name(self, name: str) -> SkillInfo | None:
        """Get skill by name."""
        return next((skill for skill in self.skills if skill.name == name), None)

    @property
    def name(self) -> str:
        """Get character name."""
        return self.id.name

    @property
    def entry_id(self) -> str:
        """Get character entry ID."""
        return self.id.entry_id


@dataclass
class Artifact:
    """Entity representing an artifact (声骸)."""

    id: ArtifactId
    set_effects: list[ArtifactSetEffect] = field(default_factory=list)
    modules: list[ContentModule] = field(default_factory=list)
    echo_types: list[str] = field(default_factory=list)

    def add_set_effect(self, effect: ArtifactSetEffect) -> None:
        """Add a set effect to this artifact."""
        self.set_effects.append(effect)

    def get_set_effect_by_count(self, piece_count: int) -> ArtifactSetEffect | None:
        """Get set effect by piece count."""
        return next((effect for effect in self.set_effects if effect.piece_count == piece_count), None)

    def add_module(self, module: ContentModule) -> None:
        """Add a module to this artifact."""
        self.modules.append(module)

    def add_echo_type(self, echo_type: str) -> None:
        """Add an echo type to this artifact."""
        if echo_type not in self.echo_types:
            self.echo_types.append(echo_type)

    @property
    def name(self) -> str:
        """Get artifact name."""
        return self.id.name

    @property
    def entry_id(self) -> str:
        """Get artifact entry ID."""
        return self.id.entry_id


@dataclass
class MarkdownDocument:
    """Entity representing a markdown document."""

    title: str
    sections: list[MarkdownSection] = field(default_factory=list)

    def add_section(self, section: MarkdownSection) -> None:
        """Add a section to the document."""
        self.sections.append(section)

    def get_section_by_title(self, title: str) -> MarkdownSection | None:
        """Get section by title."""
        return next((section for section in self.sections if section.title == title), None)

    def to_markdown(self) -> str:
        """Convert document to markdown string."""
        lines = [f"# {self.title}", ""]

        for section in self.sections:
            # Add section header
            header_prefix = "#" * section.level
            lines.append(f"{header_prefix} {section.title}")
            lines.append("")

            # Add section content
            if section.content:
                lines.append(section.content)
                lines.append("")

        return "\n".join(lines).rstrip() + "\n"

    def __len__(self) -> int:
        """Get number of sections."""
        return len(self.sections)

    def is_empty(self) -> bool:
        """Check if document has no content."""
        return not self.sections or all(not section.content for section in self.sections)

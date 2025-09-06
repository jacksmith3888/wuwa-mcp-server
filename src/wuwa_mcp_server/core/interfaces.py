"""Abstract interfaces for WuWa MCP Server components."""

from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Protocol


class APIClientProtocol(Protocol):
    """Protocol for API client implementations."""

    async def fetch_character_list(self) -> list[dict[str, Any]] | None:
        """Fetch list of characters."""
        ...

    async def fetch_artifacts_list(self) -> list[dict[str, Any]] | None:
        """Fetch list of artifacts."""
        ...

    async def fetch_entry_detail(self, entry_id: str) -> dict[str, Any] | None:
        """Fetch detailed entry information."""
        ...


class ContentParserProtocol(Protocol):
    """Protocol for content parser implementations."""

    def parse_main_content(self, content_data: dict[str, Any]) -> dict[str, Any]:
        """Parse main content data."""
        ...

    def parse_character_profile(self, content_data: dict[str, Any]) -> dict[str, Any]:
        """Parse character profile data."""
        ...

    def parse_strategy_content(self, content_data: dict[str, Any]) -> dict[str, Any]:
        """Parse strategy content data."""
        ...


class MarkdownGeneratorProtocol(Protocol):
    """Protocol for markdown generator implementations."""

    def generate(self, data: dict[str, Any]) -> str:
        """Generate markdown from structured data."""
        ...


class RepositoryProtocol(Protocol):
    """Base protocol for repository implementations."""

    async def find_by_name(self, name: str) -> dict[str, Any] | None:
        """Find item by name."""
        ...


class CharacterRepositoryProtocol(RepositoryProtocol):
    """Protocol for character repository."""

    async def get_character_list(self) -> list[dict[str, Any]]:
        """Get list of all characters."""
        ...

    async def get_character_detail(self, entry_id: str) -> dict[str, Any] | None:
        """Get character detail by entry ID."""
        ...


class ArtifactRepositoryProtocol(RepositoryProtocol):
    """Protocol for artifact repository."""

    async def get_artifact_list(self) -> list[dict[str, Any]]:
        """Get list of all artifacts."""
        ...

    async def get_artifact_detail(self, entry_id: str) -> dict[str, Any] | None:
        """Get artifact detail by entry ID."""
        ...


class ServiceProtocol(Protocol):
    """Base protocol for service implementations."""

    pass


class CharacterServiceProtocol(ServiceProtocol):
    """Protocol for character service."""

    async def get_character_info(self, character_name: str) -> str:
        """Get comprehensive character information."""
        ...

    async def get_character_profile(self, character_name: str) -> str:
        """Get character profile information."""
        ...


class ArtifactServiceProtocol(ServiceProtocol):
    """Protocol for artifact service."""

    async def get_artifact_info(self, artifact_name: str) -> str:
        """Get artifact information."""
        ...


class MarkdownServiceProtocol(ServiceProtocol):
    """Protocol for markdown service."""

    def generate_character_markdown(self, parsed_data: dict[str, Any], include_strategy: bool = True) -> str:
        """Generate markdown for character data."""
        ...

    def generate_artifact_markdown(self, parsed_data: dict[str, Any]) -> str:
        """Generate markdown for artifact data."""
        ...

    def generate_strategy_markdown(self, parsed_data: dict[str, Any]) -> str:
        """Generate markdown for strategy data."""
        ...


class HTTPClientProtocol(Protocol):
    """Protocol for HTTP client implementations."""

    async def get(self, url: str, **kwargs) -> dict[str, Any]:
        """Perform HTTP GET request."""
        ...

    async def post(self, url: str, **kwargs) -> dict[str, Any]:
        """Perform HTTP POST request."""
        ...

    async def close(self) -> None:
        """Close the HTTP client."""
        ...


# Abstract base classes


class BaseRepository(ABC):
    """Base repository abstract class."""

    @abstractmethod
    async def find_by_name(self, name: str) -> dict[str, Any] | None:
        """Find item by name."""
        pass


class BaseContentParser(ABC):
    """Base content parser abstract class."""

    @abstractmethod
    def parse(self, content_data: dict[str, Any]) -> dict[str, Any]:
        """Parse content data."""
        pass


class BaseMarkdownComponent(ABC):
    """Base markdown component abstract class."""

    @abstractmethod
    def generate(self, data: Any) -> str:
        """Generate markdown for this component."""
        pass


class BaseService(ABC):
    """Base service abstract class."""

    pass


class BaseHTMLConverter(ABC):
    """Base HTML to Markdown converter abstract class."""

    @abstractmethod
    def convert(self, html_content: str) -> str:
        """Convert HTML content to markdown."""
        pass

    @abstractmethod
    def extract_tables(self, html_content: str) -> list[list[list[str]]]:
        """Extract tables from HTML content."""
        pass


class BaseParsingStrategy(ABC):
    """Base parsing strategy for different content types."""

    @abstractmethod
    def can_handle(self, content_type: str) -> bool:
        """Check if this strategy can handle the content type."""
        pass

    @abstractmethod
    def parse(self, content_data: dict[str, Any]) -> dict[str, Any]:
        """Parse content using this strategy."""
        pass

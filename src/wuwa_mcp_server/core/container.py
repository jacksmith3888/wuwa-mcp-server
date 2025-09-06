"""Dependency injection container for managing component dependencies."""

from typing import Any

from ..builders.markdown_builder import MarkdownBuilder
from ..infrastructure.api.http_client import HTTPClient
from ..infrastructure.api.kuro_api_client import KuroAPIClient
from ..infrastructure.repositories.artifact_repository import ArtifactRepository
from ..infrastructure.repositories.character_repository import CharacterRepository
from ..parsers.content_parser import StrategyBasedContentParser
from ..parsers.html_converter import HTMLToMarkdownConverter
from ..services.artifact_service import ArtifactService
from ..services.character_service import CharacterService
from ..services.markdown_service import MarkdownService
from .config import ApplicationSettings
from .logging_config import LoggerMixin


class DIContainer(LoggerMixin):
    """Dependency injection container for managing object dependencies."""

    def __init__(self, settings: ApplicationSettings | None = None):
        """Initialize the container.

        Args:
            settings: Application settings. Creates default if None.
        """
        self.settings = settings or ApplicationSettings()
        self._instances: dict[str, Any] = {}
        self._singletons: dict[str, Any] = {}
        self.logger.info("Dependency injection container initialized")

    def get_settings(self) -> ApplicationSettings:
        """Get application settings.

        Returns:
            Application settings instance.
        """
        return self.settings

    def get_http_client(self) -> HTTPClient:
        """Get HTTP client instance (singleton).

        Returns:
            HTTPClient instance.
        """
        if "http_client" not in self._singletons:
            self.logger.debug("Creating HTTP client instance")
            self._singletons["http_client"] = HTTPClient(
                api_settings=self.settings.api,
                http_settings=self.settings.http_client,
                enable_circuit_breaker=True,
            )
        return self._singletons["http_client"]

    def get_kuro_api_client(self) -> KuroAPIClient:
        """Get Kuro API client instance (singleton).

        Returns:
            KuroAPIClient instance.
        """
        if "kuro_api_client" not in self._singletons:
            self.logger.debug("Creating Kuro API client instance")
            self._singletons["kuro_api_client"] = KuroAPIClient(
                http_client=self.get_http_client(),
                settings=self.settings.api,
            )
        return self._singletons["kuro_api_client"]

    def get_html_converter(self) -> HTMLToMarkdownConverter:
        """Get HTML converter instance (singleton).

        Returns:
            HTMLToMarkdownConverter instance.
        """
        if "html_converter" not in self._singletons:
            self.logger.debug("Creating HTML converter instance")
            self._singletons["html_converter"] = HTMLToMarkdownConverter()
        return self._singletons["html_converter"]

    def get_content_parser(self) -> StrategyBasedContentParser:
        """Get content parser instance (singleton).

        Returns:
            StrategyBasedContentParser instance.
        """
        if "content_parser" not in self._singletons:
            self.logger.debug("Creating strategy-based content parser instance")
            self._singletons["content_parser"] = StrategyBasedContentParser(html_converter=self.get_html_converter())
        return self._singletons["content_parser"]

    def get_markdown_builder(self) -> MarkdownBuilder:
        """Get markdown builder instance (new instance each time).

        Returns:
            MarkdownBuilder instance.
        """
        self.logger.debug("Creating markdown builder instance")
        return MarkdownBuilder()

    def get_character_repository(self) -> CharacterRepository:
        """Get character repository instance (singleton).

        Returns:
            CharacterRepository instance.
        """
        if "character_repository" not in self._singletons:
            self.logger.debug("Creating character repository instance")
            self._singletons["character_repository"] = CharacterRepository(api_client=self.get_kuro_api_client())
        return self._singletons["character_repository"]

    def get_artifact_repository(self) -> ArtifactRepository:
        """Get artifact repository instance (singleton).

        Returns:
            ArtifactRepository instance.
        """
        if "artifact_repository" not in self._singletons:
            self.logger.debug("Creating artifact repository instance")
            self._singletons["artifact_repository"] = ArtifactRepository(api_client=self.get_kuro_api_client())
        return self._singletons["artifact_repository"]

    def get_markdown_service(self) -> MarkdownService:
        """Get markdown service instance (singleton).

        Returns:
            MarkdownService instance.
        """
        if "markdown_service" not in self._singletons:
            self.logger.debug("Creating markdown service instance")
            self._singletons["markdown_service"] = MarkdownService()
        return self._singletons["markdown_service"]

    def get_character_service(self) -> CharacterService:
        """Get character service instance (singleton).

        Returns:
            CharacterService instance.
        """
        if "character_service" not in self._singletons:
            self.logger.debug("Creating character service instance")
            self._singletons["character_service"] = CharacterService(
                character_repository=self.get_character_repository(),
                content_parser=self.get_content_parser(),
                markdown_service=self.get_markdown_service(),
            )
        return self._singletons["character_service"]

    def get_artifact_service(self) -> ArtifactService:
        """Get artifact service instance (singleton).

        Returns:
            ArtifactService instance.
        """
        if "artifact_service" not in self._singletons:
            self.logger.debug("Creating artifact service instance")
            self._singletons["artifact_service"] = ArtifactService(
                artifact_repository=self.get_artifact_repository(),
                content_parser=self.get_content_parser(),
                markdown_service=self.get_markdown_service(),
            )
        return self._singletons["artifact_service"]

    def register_instance(self, name: str, instance: Any) -> None:
        """Register a specific instance with the container.

        Args:
            name: Name to register the instance under.
            instance: Instance to register.
        """
        self._instances[name] = instance
        self.logger.debug(f"Registered instance: {name}")

    def get_instance(self, name: str) -> Any:
        """Get a registered instance by name.

        Args:
            name: Name of the instance to retrieve.

        Returns:
            The registered instance.

        Raises:
            KeyError: If the instance is not found.
        """
        if name in self._instances:
            return self._instances[name]
        raise KeyError(f"Instance '{name}' not found in container")

    def clear_singletons(self) -> None:
        """Clear all singleton instances (useful for testing)."""
        self.logger.debug("Clearing singleton instances")
        self._singletons.clear()
        self._instances.clear()

    async def cleanup(self) -> None:
        """Clean up resources (close connections, etc.)."""
        self.logger.info("Cleaning up container resources")

        # HTTP clientのクリーンアップ
        if "http_client" in self._singletons:
            http_client = self._singletons["http_client"]
            if hasattr(http_client, "close"):
                await http_client.close()

        # Kuro API clientのクリーンアップ
        if "kuro_api_client" in self._singletons:
            api_client = self._singletons["kuro_api_client"]
            if hasattr(api_client, "__aexit__"):
                await api_client.__aexit__(None, None, None)

        self.clear_singletons()
        self.logger.info("Container cleanup completed")


# グローバルコンテナーインスタンス（便利な使用法）
_global_container: DIContainer | None = None


def get_container(settings: ApplicationSettings | None = None) -> DIContainer:
    """Get the global container instance.

    Args:
        settings: Application settings for initial setup.

    Returns:
        Global DIContainer instance.
    """
    global _global_container
    if _global_container is None:
        _global_container = DIContainer(settings)
    return _global_container


def reset_container() -> None:
    """Reset the global container (useful for testing)."""
    global _global_container
    if _global_container:
        _global_container.clear_singletons()
    _global_container = None


# Factory functions for easy integration
def create_character_service(container: DIContainer | None = None) -> CharacterService:
    """Create character service using dependency injection.

    Args:
        container: DI container. Uses global container if None.

    Returns:
        CharacterService instance.
    """
    if container is None:
        container = get_container()
    return container.get_character_service()


def create_artifact_service(container: DIContainer | None = None) -> ArtifactService:
    """Create artifact service using dependency injection.

    Args:
        container: DI container. Uses global container if None.

    Returns:
        ArtifactService instance.
    """
    if container is None:
        container = get_container()
    return container.get_artifact_service()

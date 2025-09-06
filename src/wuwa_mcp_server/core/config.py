"""Configuration management for WuWa MCP Server."""

import os


class APISettings:
    """Kuro BBS API related settings."""

    def __init__(self):
        self.base_url: str = os.getenv("KURO_API_BASE_URL", "https://api.kurobbs.com/wiki/core/catalogue/item")
        self.character_catalogue_id: str = os.getenv("KURO_API_CHARACTER_CATALOGUE_ID", "1105")
        self.artifacts_catalogue_id: str = os.getenv("KURO_API_ARTIFACTS_CATALOGUE_ID", "1219")
        self.default_page: str = os.getenv("KURO_API_DEFAULT_PAGE", "1")
        self.default_limit: str = os.getenv("KURO_API_DEFAULT_LIMIT", "1000")
        self.timeout: float = float(os.getenv("KURO_API_TIMEOUT", "30.0"))
        self.retry_attempts: int = int(os.getenv("KURO_API_RETRY_ATTEMPTS", "3"))
        self.retry_delay: float = float(os.getenv("KURO_API_RETRY_DELAY", "1.0"))


class ServerSettings:
    """Server related settings."""

    def __init__(self):
        self.transport: str = os.getenv("TRANSPORT", "stdio")
        self.host: str = os.getenv("HOST", "0.0.0.0")
        self.port: int = int(os.getenv("PORT", "8081"))


class LogSettings:
    """Logging related settings."""

    def __init__(self):
        self.level: str = os.getenv("LOG_LEVEL", "INFO")
        self.format: str = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        self.disable_uvicorn_logs: bool = os.getenv("DISABLE_UVICORN_LOGS", "true").lower() == "true"


class HTTPClientSettings:
    """HTTP client related settings."""

    def __init__(self):
        self.user_agent: str = os.getenv(
            "HTTP_CLIENT_USER_AGENT",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        )
        self.origin: str = os.getenv("HTTP_CLIENT_ORIGIN", "https://wiki.kurobbs.com")
        self.referer: str = os.getenv("HTTP_CLIENT_REFERER", "https://wiki.kurobbs.com/")
        self.source: str = os.getenv("HTTP_CLIENT_SOURCE", "h5")
        self.content_type: str = os.getenv(
            "HTTP_CLIENT_CONTENT_TYPE", "application/x-www-form-urlencoded;charset=UTF-8"
        )
        self.accept: str = os.getenv("HTTP_CLIENT_ACCEPT", "application/json, text/plain, */*")
        self.accept_encoding: str = os.getenv("HTTP_CLIENT_ACCEPT_ENCODING", "gzip, deflate, br, zstd")
        self.wiki_type: str = os.getenv("HTTP_CLIENT_WIKI_TYPE", "9")

        # Additional settings for the enhanced HTTP client
        self.timeout: float = float(os.getenv("HTTP_CLIENT_TIMEOUT", "30.0"))
        self.max_retries: int = int(os.getenv("HTTP_CLIENT_MAX_RETRIES", "3"))
        self.retry_delay: float = float(os.getenv("HTTP_CLIENT_RETRY_DELAY", "1.0"))
        self.circuit_breaker_threshold: int = int(os.getenv("HTTP_CLIENT_CIRCUIT_BREAKER_THRESHOLD", "5"))
        self.circuit_breaker_timeout: float = float(os.getenv("HTTP_CLIENT_CIRCUIT_BREAKER_TIMEOUT", "60.0"))


class ApplicationSettings:
    """Main application settings."""

    def __init__(self):
        # App info
        self.app_name: str = "WuWa MCP Server"
        self.version: str = "2.0.1"
        self.debug: bool = os.getenv("DEBUG", "false").lower() == "true"

        # Sub-settings
        self.api: APISettings = APISettings()
        self.server: ServerSettings = ServerSettings()
        self.logging: LogSettings = LogSettings()
        self.http_client: HTTPClientSettings = HTTPClientSettings()

    def get_http_headers(self) -> dict[str, str]:
        """Get HTTP headers for API requests."""
        return {
            "User-Agent": self.http_client.user_agent,
            "Origin": self.http_client.origin,
            "Referer": self.http_client.referer,
            "Source": self.http_client.source,
            "Content-Type": self.http_client.content_type,
            "Accept": self.http_client.accept,
            "Accept-Encoding": self.http_client.accept_encoding,
            "wiki_type": self.http_client.wiki_type,
        }


# Global settings instance
_settings: ApplicationSettings | None = None


def get_settings() -> ApplicationSettings:
    """Get application settings singleton."""
    global _settings
    if _settings is None:
        _settings = ApplicationSettings()
    return _settings


# Alias for compatibility with container
def get_application_settings() -> ApplicationSettings:
    """Get application settings (alias for get_settings)."""
    return get_settings()

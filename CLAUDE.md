# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Model Context Protocol (MCP) server for the game "鸣潮" (Wuthering Waves) that provides character and artifact information in Markdown format, optimized for Large Language Model consumption. The project uses **uv** for package management and requires Python ≥3.12.

## Development Commands

### Setup and Installation

```bash
# Install dependencies using uv
uv sync

# Install development dependencies (including ruff for linting)
uv sync --extra dev

# Install in development mode using uv
uv pip install -e .

# Alternative: Install directly from PyPI using uv
uv pip install wuwa-mcp-server
```

### Running the Server

```bash
# Run the MCP server locally for testing
uv run python -m wuwa_mcp_server.server

# Or run with uvx (recommended for end users)
uvx wuwa-mcp-server
```

### Build and Package

```bash
# Build the package using uv
uv build

# Alternative: Build using standard Python tools
python -m pip install build
python -m build
```

### Code Quality

```bash
# Format all Python code
uv run ruff format .

# Check for code issues
uv run ruff check .

# Automatically fix fixable issues
uv run ruff check --fix .
```

### Docker

```bash
# Build Docker image
docker build -t wuwa-mcp-server .

# Run Docker container (HTTP mode)
docker run -p 8081:8000 wuwa-mcp-server

# Run Docker container (STDIO mode)
docker run -e TRANSPORT=stdio wuwa-mcp-server
```

### Publishing

- Releases are automatically published to PyPI via GitHub Actions when a release is created
- Package is available via Smithery registry for easy installation

## Architecture Overview

The project follows a **Domain-Driven Design (DDD)** architecture with clear separation of concerns:

### Core Components

1. **Server (`server.py`)**
   - FastMCP-based MCP server with three main tools
   - Dependency Injection container for service management
   - Handles both STDIO and HTTP transport modes
   - Main entry point: `main()` function

2. **Core Layer (`core/`)**
   - **Configuration**: Application settings and HTTP client configuration
   - **Dependency Injection**: DIContainer for managing service dependencies
   - **Interfaces**: Protocols defining contracts for repositories and services
   - **Exceptions**: Custom exception hierarchy for error handling
   - **Logging**: Structured logging configuration

3. **Domain Layer (`domain/`)**
   - **Entities**: Character, Artifact, and MarkdownDocument domain objects
   - **Value Objects**: Strongly-typed identifiers and data structures
   - Pure business logic with no external dependencies

4. **Infrastructure Layer (`infrastructure/`)**
   - **API Client**: KuroAPIClient for Kuro BBS Wiki API communication
   - **HTTP Client**: Low-level HTTP communication with retry logic
   - **Repositories**: Data access implementations for characters and artifacts

5. **Services Layer (`services/`)**
   - **Character Service**: Business logic for character data processing
   - **Artifact Service**: Business logic for artifact data processing  
   - **Markdown Service**: Converts processed data to optimized Markdown

6. **Parsers (`parsers/`)**
   - **Content Parser**: Converts JSON/HTML data to structured format
   - **HTML Converter**: BeautifulSoup-based HTML to Markdown conversion
   - **Strategy Pattern**: Different parsing strategies for various content types

7. **Builders (`builders/`)**
   - **Markdown Builder**: Builder pattern for flexible document construction
   - **Markdown Formatter**: Handles tables, lists, and formatting

### Data Flow

1. **Character Info**: `get_character_info()` → Fetch character list → Find match → Get profile data → Extract strategy ID → Parallel fetch strategy + parse profile → Combine Markdown
2. **Artifact Info**: `get_artifact_info()` → Fetch artifact list → Find match → Get detail data → Parse → Generate Markdown
3. **Character Profile**: `get_character_profile()` → Same as character info but only profile data

### Key Design Patterns

- **Async Context Managers**: `KuroWikiApiClient` uses `__aenter__`/`__aexit__`
- **Parallel Processing**: Character info fetches strategy data while parsing profile
- **Thread Pool**: CPU-intensive parsing uses `asyncio.to_thread()`
- **Error Handling**: Graceful fallbacks with Chinese error messages

## MCP Tools Available

### 1. get_character_info

```python
async def get_character_info(character_name: str) -> str
```

- Comprehensive character data including skills, development guides, and strategy
- Combines profile and strategy content in single response
- **Parameter**: `character_name` - Chinese name of the character to query
- **Returns**: Markdown string with character information

### 2. get_artifact_info

```python
async def get_artifact_info(artifact_name: str) -> str
```

- Detailed artifact set (声骸) information and stats
- **Parameter**: `artifact_name` - Chinese name of the artifact set to query
- **Returns**: Markdown string with artifact information

### 3. get_character_profile

```python
async def get_character_profile(character_name: str) -> str
```

- Character profile/档案 information only (subset of full character info)
- Lighter weight alternative to full character info
- **Parameter**: `character_name` - Chinese name of the character to query
- **Returns**: Markdown string with character profile information

## Installation for End Users

### Via Smithery (Recommended)

```bash
npx -y @smithery/cli@latest install @jacksmith3888/wuwa-mcp-server --client claude --key YOUR_SMITHERY_KEY
```

### Via uv

```bash
uv pip install wuwa-mcp-server
```

### Claude Desktop Configuration

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "wuwa-mcp": {
      "command": "uvx",
      "args": ["wuwa-mcp-server"]
    }
  }
}
```

### Cherry Studio Configuration

```json
{
  "mcpServers": {
    "wuwa-mcp": {
      "command": "uvx",
      "args": ["wuwa-mcp-server"]
    }
  }
}
```

## Configuration Files

- **pyproject.toml**: Python packaging with uv support, requires Python ≥3.12
- **uv.lock**: Dependency lock file for reproducible builds
- **.python-version**: Specifies Python 3.12 requirement
- **smithery.yaml**: Smithery MCP registry configuration
- **Dockerfile**: Multi-stage build with uv optimization for containerized deployment
- **.github/workflows/python-publish.yml**: Automated PyPI publishing on release

## Development Notes

- Project uses **uv** for package management, not pip
- **Code Quality**: Uses **ruff** for linting and formatting with Python 3.12+ modern syntax
  - Line length: 120 characters
  - Modern type annotations (dict/list instead of Dict/List)
  - Import sorting with single-line imports
  - Comprehensive rule set: pycodestyle, pyflakes, isort, naming, pyupgrade, bugbear, etc.
- Multi-stage Docker build optimized with uv for faster builds and smaller images
- Smithery deployment configured for custom container runtime with HTTP transport
- No tests currently exist in the codebase
- Error messages are in Chinese for user-facing responses
- Debug prints are in English for development
- All API responses use Chinese field names and content
- FastMCP handles the MCP protocol implementation
- HTTP timeout set to 30 seconds for API calls
- Data source: 库街区 (Kujiequ) API at `https://api.kurobbs.com/wiki/core/catalogue/item`

## Recent Updates (v2.0.0)

- **Architecture Refactor**: Complete rewrite using Domain-Driven Design (DDD) with layered architecture
- **Code Quality**: Added ruff for linting and formatting with comprehensive rule set
- **Modern Python**: Updated to use Python 3.12+ features and modern type annotations
- **Dependency Injection**: Implemented DI container for better service management
- **Legacy Cleanup**: Removed old implementation files and consolidated functionality
- **Smithery Configuration**: Fixed `smithery.yaml` for proper custom container deployment
- **Docker Optimization**: Updated Dockerfile to use uv with multi-stage build for better performance
- **Port Configuration**: Fixed HTTP server to bind to `0.0.0.0:8081` for container compatibility
- **Transport Handling**: Improved environment variable handling for both STDIO and HTTP modes

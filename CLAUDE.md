# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Model Context Protocol (MCP) server for the game "鸣潮" (Wuthering Waves) that provides character and artifact information in Markdown format, optimized for Large Language Model consumption. The project uses **uv** for package management and requires Python ≥3.12.

## Development Commands

### Setup and Installation

```bash
# Install dependencies using uv
uv sync

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

### Docker

```bash
# Build Docker image
docker build -t wuwa-mcp-server .

# Run Docker container
docker run wuwa-mcp-server
```

### Publishing

- Releases are automatically published to PyPI via GitHub Actions when a release is created
- Package is available via Smithery registry for easy installation

## Architecture Overview

### Core Components

1. **Server (`server.py`)**

   - FastMCP-based MCP server with three main tools
   - Handles async/await patterns for API calls
   - Implements parallel processing for character data fetching
   - Main entry point: `main()` function

2. **API Client (`api_client.py`)**

   - `KuroWikiApiClient`: Async HTTP client for Kuro BBS Wiki API
   - Context manager pattern for proper resource management
   - Fetches character lists, artifact lists, and detailed entry data
   - Base URL: `https://api.kurobbs.com/wiki/core/catalogue/item`
   - Character catalogue ID: `1105`, Artifacts catalogue ID: `1219`

3. **Content Parser (`content_parser.py`)**

   - `ContentParser`: Converts JSON/HTML data to structured format
   - Module types: `CHARACTER_DATA`, `CHARACTER_DEVELOPMENT`, `CHARACTER_STRATEGY`
   - HTML-to-Markdown conversion with BeautifulSoup
   - Special handling for different content types (profile vs strategy)

4. **Markdown Generator (`markdown_generator.py`)**
   - `convert_to_markdown()`: Final step to generate LLM-optimized Markdown
   - Handles deduplication and proper formatting
   - Special formatting for character data, tables, and strategy links

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
- **Dockerfile**: Multi-stage build for containerized deployment
- **.github/workflows/python-publish.yml**: Automated PyPI publishing on release

## Development Notes

- Project uses **uv** for package management, not pip
- No tests currently exist in the codebase
- Error messages are in Chinese for user-facing responses
- Debug prints are in English for development
- All API responses use Chinese field names and content
- FastMCP handles the MCP protocol implementation
- HTTP timeout set to 30 seconds for API calls
- Data source: 库街区 (Kujiequ) API at `https://api.kurobbs.com/wiki/core/catalogue/item`

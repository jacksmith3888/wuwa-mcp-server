# Wuthering Waves MCP Server

[![smithery badge](https://smithery.ai/badge/@jacksmith3888/wuwa-mcp-server)](https://smithery.ai/server/@jacksmith3888/wuwa-mcp-server)

A Model Context Protocol (MCP) server for fetching character and echo information from the Wuthering Waves game, returning results in Markdown format optimized for Large Language Model consumption.

**🇺🇸 English Documentation | 📄 [中文文档](README.md)**

## 🚀 Latest Updates (v1.1.0)

- ✅ **Streamable HTTP Transport Support**: Now supports Smithery's new HTTP transport protocol
- 🔄 **Backward Compatible**: Supports both traditional STDIO and new HTTP transport modes
- 🌐 **Cloud Deployment Ready**: Perfect for VPS, Google Cloud Run, AWS Lambda, and other cloud environments
- 📦 **Dependency Updates**: Upgraded to MCP 1.13.1 with latest transport protocol support

## Features

- **Character Information Query**: Fetch detailed information about Wuthering Waves characters
- **Echo Information Query**: Get detailed information about echo sets in Wuthering Waves
- **Character Profile Query**: Retrieve character profile information from Wuthering Waves
- **LLM-Optimized Output**: Results formatted specifically for Large Language Model consumption
- **Dual Transport Modes**: Supports both STDIO and Streamable HTTP transports

## Installation

### Install via Smithery

To automatically install the WuWa MCP Server through [Smithery](https://smithery.ai/server/@jacksmith3888/wuwa-mcp-server):

```bash
npx -y @smithery/cli@latest install @jacksmith3888/wuwa-mcp-server --client claude --key YOUR_SMITHERY_KEY
```

### Install via `uv`

Install directly from PyPI:

```bash
uv pip install wuwa-mcp-server
```

## Usage

### Running with Cherry Studio

1. Download [Cherry Studio](https://github.com/CherryHQ/cherry-studio)
2. Go to Settings and click on MCP Servers

Add the following configuration:

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

### Running with Claude Desktop

1. Download [Claude Desktop](https://claude.ai/download)
2. Create or edit your Claude Desktop configuration file:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\\Claude\\claude_desktop_config.json`

Add the following configuration:

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

3. Restart Claude Desktop

## Available Tools

### 1. Character Information Tool

```python
async def get_character_info(character_name: str) -> str
```

Query detailed character information from KujieQu and return in Markdown format.

**Parameters:**

- `character_name`: The Chinese name of the character to query

**Returns:**
Markdown string containing character information, or error message if character not found or data fetch failed.

### 2. Echo Information Tool

```python
async def get_artifact_info(artifact_name: str) -> str
```

Query detailed echo information from KujieQu and return in Markdown format.

**Parameters:**

- `artifact_name`: The Chinese name of the echo set to query

**Returns:**
Markdown string containing echo information, or error message if echo not found or data fetch failed.

### 3. Character Profile Tool

```python
async def get_character_profile(character_name: str) -> str
```

Query character profile information from KujieQu and return in Markdown format.

**Parameters:**

- `character_name`: The Chinese name of the character to query

**Returns:**
Markdown string containing character profile information, or error message if character not found or data fetch failed.

## Development and Testing

### Local Development

```bash
# STDIO mode (default)
uv run python -m wuwa_mcp_server.server

# HTTP mode
TRANSPORT=http uv run python -m wuwa_mcp_server.server
```

### Docker Deployment

```bash
# Build image
docker build -t wuwa-mcp-server .

# Run container (HTTP mode)
docker run -p 8081:8081 wuwa-mcp-server

# Run container (STDIO mode)
docker run -e TRANSPORT=stdio wuwa-mcp-server
```

## Technical Details

### Data Processing

- Clean and format KujieQu data
- Optimize format for LLM consumption
- Support parallel processing for improved performance
- Asynchronous operations to avoid blocking

### Transport Modes

- **STDIO Transport**: Suitable for local clients like Claude Desktop
- **Streamable HTTP Transport**: Suitable for cloud deployment and remote access
- Automatic detection via `TRANSPORT` environment variable

## Contributing

Issues and pull requests are welcome! Some potential areas for improvement:

- Add support for more Wuthering Waves game content
- Enhance content parsing options
- Add caching layer for frequently accessed content
- Support for additional language localizations

## License

This project is licensed under the MIT License.
[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/jacksmith3888-wuwa-mcp-server-badge.png)](https://mseep.ai/app/jacksmith3888-wuwa-mcp-server)

# 鸣潮 MCP Server

[![smithery badge](https://smithery.ai/badge/@jacksmith3888/wuwa-mcp-server)](https://smithery.ai/server/@jacksmith3888/wuwa-mcp-server)

一个 Model Context Protocol (MCP) 服务器，用于获取《鸣潮》游戏的角色和声骸信息，并以 Markdown 格式返回，方便大型语言模型使用。

## 功能特点

- **角色信息查询**：获取《鸣潮》游戏中角色的详细信息
- **声骸信息查询**：获取《鸣潮》游戏中声骸套装的详细信息
- **角色档案查询**：获取《鸣潮》游戏中角色的档案信息
- **LLM 友好输出**：结果格式特别为大型语言模型优化

## 安装方法

### 通过 Smithery 安装

要通过 [Smithery](https://smithery.ai/server/@jason/wuwa-mcp-server) 自动安装 WuWa MCP Server：

```bash
npx -y @smithery/cli@latest install @jacksmith3888/wuwa-mcp-server --client claude --key YOUR_SMITHERY_KEYs
```

### 通过 `uv` 安装

直接从 PyPI 安装：

```bash
uv pip install wuwa-mcp-server
```

## 使用方法

### 与 Cherry Studio 一起运行

1. 下载 [Cherry Studio](https://github.com/CherryHQ/cherry-studio)
2. 在设置中点击 MCP 服务器

添加以下配置：

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

### 与 Claude Desktop 一起运行

1. 下载 [Claude Desktop](https://claude.ai/download)
2. 创建或编辑您的 Claude Desktop 配置文件：
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\\Claude\\claude_desktop_config.json`

添加以下配置：

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

3. 重启 Claude Desktop

## 可用工具

### 1. 角色信息工具

```python
async def get_character_info(character_name: str) -> str
```

在库街区上查询角色详细信息并以 Markdown 格式返回。

**参数：**

- `character_name`: 要查询的角色的中文名称

**返回：**
包含角色信息的 Markdown 字符串，或者在找不到角色或获取数据失败时返回错误消息。

### 2. 声骸信息工具

```python
async def get_artifact_info(artifact_name: str) -> str
```

在库街区上查询声骸详细信息并以 Markdown 格式返回。

**参数：**

- `artifact_name`: 要查询的声骸套装的中文名称

**返回：**
包含声骸信息的 Markdown 字符串，或者在找不到声骸或获取数据失败时返回错误消息。

### 3. 角色档案工具

```python
async def get_character_profile(character_name: str) -> str
```

在库街区上查询角色档案信息并以 Markdown 格式返回。

**参数：**

- `character_name`: 要查询的角色的中文名称

**返回：**
包含角色档案信息的 Markdown 字符串，或者在找不到角色或获取数据失败时返回错误消息。

## 详细功能

### 结果处理

- 清理和格式化库街区数据
- 为 LLM 消费优化格式

## 贡献

欢迎提出问题和拉取请求！一些潜在的改进领域：

- 增加对更多《鸣潮》游戏内容的支持
- 增强内容解析选项
- 增加对频繁访问内容的缓存层

## 许可证

本项目采用 MIT 许可证。

# 鸣潮 MCP Server

[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/jacksmith3888-wuwa-mcp-server-badge.png)](https://mseep.ai/app/jacksmith3888-wuwa-mcp-server)

[![smithery badge](https://smithery.ai/badge/@jacksmith3888/wuwa-mcp-server)](https://smithery.ai/server/@jacksmith3888/wuwa-mcp-server)

一个 Model Context Protocol (MCP) 服务器，用于获取《鸣潮》游戏的角色和声骸信息，并以 Markdown 格式返回，方便大型语言模型使用。

**📄 [English Documentation](README_EN.md) | 🇨🇳 中文文档**

## 🚀 最新更新 (v2.0.1)

- 🏗️ **架构重构**：采用领域驱动设计（DDD）架构，清晰的分层结构
- 🔧 **代码质量**：集成 ruff 代码格式化和静态分析工具
- 📝 **现代化语法**：使用 Python 3.12+ 现代类型注解 (dict/list 替代 Dict/List)
- 🧹 **代码清理**：移除旧有代码，统一代码风格和质量标准
- ✅ **支持 Streamable HTTP 传输**：支持 Smithery 的新 HTTP 传输协议
- 🔄 **向后兼容**：同时支持传统的 STDIO 和新的 HTTP 传输模式
- 🌐 **云端部署就绪**：完美适配 VPS、Google Cloud Run、AWS Lambda 等云环境
- 📦 **依赖注入**：使用依赖注入容器管理服务实例
- 🐳 **Docker 优化**：使用 uv 的多阶段构建，提升构建速度并减小镜像体积

## 功能特点

- **角色信息查询**：获取《鸣潮》游戏中角色的详细信息
- **声骸信息查询**：获取《鸣潮》游戏中声骸套装的详细信息
- **角色档案查询**：获取《鸣潮》游戏中角色的档案信息
- **LLM 友好输出**：结果格式特别为大型语言模型优化
- **双传输模式**：支持 STDIO 和 Streamable HTTP 传输

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

## 开发和测试

### 本地运行

```bash
# STDIO 模式（默认）
uv run python -m wuwa_mcp_server.server

# HTTP 模式
TRANSPORT=http uv run python -m wuwa_mcp_server.server
```

### 代码质量

项目使用 **ruff** 进行代码格式化和静态分析，确保代码质量和一致性。

#### 安装开发依赖

```bash
uv sync --extra dev
```

#### 代码格式化和检查

```bash
# 格式化所有 Python 代码
uv run ruff format .

# 检查代码问题
uv run ruff check .

# 自动修复可修复的问题
uv run ruff check --fix .
```

#### Ruff 配置

项目配置了以下代码质量规则：

- **行长度**: 120 字符
- **目标 Python 版本**: 3.12
- **启用规则**: pycodestyle、pyflakes、isort、命名约定、pyupgrade、bugbear、代码简化等
- **Import 排序**: 强制单行导入，项目模块优先级设置

### Docker 部署

```bash
# 构建镜像
docker build -t wuwa-mcp-server .

# 运行容器（HTTP 模式）
docker run -p 8081:8000 wuwa-mcp-server

# 运行容器（STDIO 模式）
docker run -e TRANSPORT=stdio wuwa-mcp-server
```

## 详细功能

### 结果处理

- 清理和格式化库街区数据
- 为 LLM 消费优化格式
- 支持并行处理提高性能
- 异步操作避免阻塞

### 传输模式

- **STDIO 传输**：适用于本地客户端，如 Claude Desktop
- **Streamable HTTP 传输**：适用于云端部署和远程访问
- 自动检测环境变量 `TRANSPORT` 切换模式

## 贡献

欢迎提出问题和拉取请求！一些潜在的改进领域：

- 增加对更多《鸣潮》游戏内容的支持
- 增强内容解析选项
- 增加对频繁访问内容的缓存层
- 支持更多语言的本地化

## 许可证

本项目采用 MIT 许可证。

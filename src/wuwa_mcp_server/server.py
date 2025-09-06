import asyncio
import os

from mcp.server.fastmcp import FastMCP

from .core import DIContainer
from .core import get_container
from .core.exceptions import DataNotFoundException
from .core.exceptions import ServiceException

# Initialize FastMCP
mcp = FastMCP("wuwa-mcp-server")

# Global container for dependency injection
container: DIContainer | None = None


def get_services():
    """Get service instances from the DI container."""
    global container
    if container is None:
        container = get_container()

    character_service = container.get_character_service()
    artifact_service = container.get_artifact_service()
    return character_service, artifact_service


@mcp.tool()
async def get_artifact_info(artifact_name: str) -> str:
    """获取库街区上的声骸详细信息并以 Markdown 格式返回。

    Args:
        artifact_name: 要查询的声骸套装的中文名称。

    Returns:
        包含声骸信息的 Markdown 字符串，
        或者在找不到声骸或获取数据失败时返回错误消息。
    """
    try:
        _, artifact_service = get_services()
        return await artifact_service.get_artifact_info(artifact_name)
    except (DataNotFoundException, ServiceException) as e:
        # These exceptions already have user-friendly messages
        return str(e)
    except Exception:
        return f"错误：处理 '{artifact_name}' 时发生意外错误。请检查服务器日志。"


@mcp.tool()
async def get_character_info(character_name: str) -> str:
    """获取库街区上的角色详细信息包括角色技能，养成攻略等，并以 Markdown 格式返回。

    Args:
        character_name: 要查询的角色的中文名称。

    Returns:
        包含角色信息的 Markdown 字符串，
        或者在找不到角色或获取数据失败时返回错误消息。
    """
    try:
        character_service, _ = get_services()
        return await character_service.get_character_info(character_name)
    except (DataNotFoundException, ServiceException) as e:
        # These exceptions already have user-friendly messages
        return str(e)
    except Exception:
        return f"错误：处理 '{character_name}' 时发生意外错误。请检查服务器日志。"


@mcp.tool()
async def get_character_profile(character_name: str) -> str:
    """获取库街区上的角色档案信息并以 Markdown 格式返回。

    Args:
        character_name: 要查询的角色的中文名称。

    Returns:
        包含角色档案信息的 Markdown 字符串，
        或者在找不到角色或获取数据失败时返回错误消息。
    """
    try:
        character_service, _ = get_services()
        return await character_service.get_character_profile(character_name)
    except (DataNotFoundException, ServiceException) as e:
        # These exceptions already have user-friendly messages
        return str(e)
    except Exception:
        return f"错误：处理 '{character_name}' 档案时发生意外错误。请检查服务器日志。"


async def cleanup_resources():
    """Clean up resources when server shuts down."""
    global container
    if container:
        await container.cleanup()


def main():
    """Main entry point. Start the appropriate transport mode based on environment variables."""
    transport_mode = os.getenv("TRANSPORT", "stdio").lower()

    try:
        if transport_mode == "http":
            print("Starting Streamable HTTP transport mode...")

            # Port and host configuration
            port = int(os.environ.get("PORT", 8081))
            host = os.environ.get("HOST", "0.0.0.0")
            print(f"Server will start on {host}:{port}")

            # Set environment variables that FastMCP/uvicorn might use
            os.environ["PORT"] = str(port)
            os.environ["HOST"] = host
            os.environ["UVICORN_HOST"] = host
            os.environ["UVICORN_PORT"] = str(port)

            # Start FastMCP with Streamable HTTP transport mode
            mcp.run(transport="streamable-http")
        else:
            print("Starting STDIO transport mode...")
            # STDIO mode (for backward compatibility with existing setups)
            mcp.run()
    finally:
        # Clean up resources on shutdown
        try:
            # Create a new event loop for cleanup if none exists
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            if loop.is_running():
                loop.create_task(cleanup_resources())
            else:
                loop.run_until_complete(cleanup_resources())
                loop.close()
        except Exception as e:
            print(f"Error during cleanup: {e}")


if __name__ == "__main__":
    main()

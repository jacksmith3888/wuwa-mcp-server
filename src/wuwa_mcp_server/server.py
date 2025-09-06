import asyncio
import os

from mcp.server.fastmcp import FastMCP

try:
    from smithery.decorators import smithery

    SMITHERY_AVAILABLE = True
except ImportError:
    SMITHERY_AVAILABLE = False

from .core import DIContainer
from .core import get_container
from .core.exceptions import DataNotFoundException
from .core.exceptions import ServiceException

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


async def cleanup_resources():
    """Clean up resources when server shuts down."""
    global container
    if container:
        await container.cleanup()


def _create_base_server():
    """Create the base MCP server with all tools."""
    mcp = FastMCP("wuwa-mcp-server")

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

    return mcp


# Create the Smithery-decorated server if available
if SMITHERY_AVAILABLE:

    @smithery.server()
    def create_server():
        """Create and configure the MCP server for Smithery deployment."""
        return _create_base_server()
else:
    # Fallback for local testing without Smithery
    def create_server():
        """Create and configure the MCP server for local testing."""
        return _create_base_server()


def main():
    """Main entry point. Start the appropriate transport mode based on environment variables."""
    # Create the server instance for local testing
    mcp = create_server()

    transport_mode = os.getenv("TRANSPORT", "stdio").lower()

    try:
        if transport_mode == "http":
            print("Starting HTTP transport mode...")

            # Port and host configuration
            port = int(os.environ.get("PORT", 8081))
            host = os.environ.get("HOST", "0.0.0.0")
            print(f"Server will start on {host}:{port}")

            # Use uvicorn directly to control host and port for HTTP mode
            import traceback

            import uvicorn

            # Get the FastMCP app configured for SSE transport
            # We'll create a simple wrapper to start the server manually
            from starlette.applications import Starlette
            from starlette.responses import JSONResponse

            # Create a custom ASGI application with proper MCP endpoints
            app = Starlette()

            # Add MCP endpoint
            @app.route("/mcp/v1", methods=["POST"])
            async def mcp_endpoint(request):
                try:
                    # Get JSON body
                    body = await request.json()

                    # Handle MCP initialization
                    if body.get("method") == "initialize":
                        return JSONResponse(
                            {
                                "jsonrpc": "2.0",
                                "id": body.get("id"),
                                "result": {
                                    "protocolVersion": "2025-06-18",
                                    "capabilities": {
                                        "experimental": {},
                                        "prompts": {"listChanged": False},
                                        "resources": {"subscribe": False, "listChanged": False},
                                        "tools": {"listChanged": False},
                                    },
                                    "serverInfo": {"name": "wuwa-mcp-server", "version": "1.13.1"},
                                },
                            }
                        )

                    # Handle tool calls
                    elif body.get("method") == "tools/call":
                        tool_name = body.get("params", {}).get("name")
                        arguments = body.get("params", {}).get("arguments", {})

                        # Get services
                        character_service, artifact_service = get_services()

                        result = ""
                        if tool_name == "get_character_info":
                            result = await character_service.get_character_info(arguments.get("character_name"))
                        elif tool_name == "get_artifact_info":
                            result = await artifact_service.get_artifact_info(arguments.get("artifact_name"))
                        elif tool_name == "get_character_profile":
                            result = await character_service.get_character_profile(arguments.get("character_name"))
                        else:
                            return JSONResponse(
                                {
                                    "jsonrpc": "2.0",
                                    "id": body.get("id"),
                                    "error": {"code": -32601, "message": "Method not found"},
                                }
                            )

                        return JSONResponse({"jsonrpc": "2.0", "id": body.get("id"), "result": result})

                    else:
                        return JSONResponse(
                            {
                                "jsonrpc": "2.0",
                                "id": body.get("id"),
                                "error": {"code": -32601, "message": "Method not found"},
                            }
                        )

                except Exception as e:
                    print(f"Error in MCP endpoint: {e}")
                    traceback.print_exc()
                    return JSONResponse(
                        {
                            "jsonrpc": "2.0",
                            "id": body.get("id", 1),
                            "error": {"code": -32603, "message": "Internal error", "data": str(e)},
                        }
                    )

            # Start uvicorn server
            uvicorn.run(app, host=host, port=port, log_level="info")
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

import contextlib
import logging
from collections.abc import AsyncIterator
from contextvars import ContextVar

import click
import mcp.types as types
from mcp.server.lowlevel import Server
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from starlette.applications import Starlette
from starlette.routing import Mount, Route
from starlette.types import Receive, Scope, Send

from src_mcp.mcp_server.manager_server_tool import EnhancedServerToolManager
from src_mcp.mcp_server.manager_tool import call_api_tool

from starlette.types import ASGIApp, Scope, Receive, Send

class PostOnlyASGIApp:
    """仅接受POST请求的ASGI包装器"""
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["method"] != "POST":
            # 直接返回405错误
            await send({
                "type": "http.response.start",
                "status": 405,
                "headers": [(b"content-type", b"text/plain")],
            })
            await send({
                "type": "http.response.body",
                "body": b"Method Not Allowed",
            })
            return
        await self.app(scope, receive, send)

class PathNormalizerASGIApp:
    """路径规范化处理器（去除末尾斜杠）"""
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        # 强制去除路径末尾斜杠
        original_path = scope["path"]
        normalized_path = original_path.rstrip("/") or "/"
        
        if original_path != normalized_path:
            # 如果原始路径不规范，直接重写scope（避免重定向）
            scope = scope.copy()
            scope["path"] = normalized_path
        
        await self.app(scope, receive, send)
        
logger = logging.getLogger(__name__)

# 创建上下文变量来存储当前请求的tool_group
current_tool_group: ContextVar[str] = ContextVar("current_tool_group", default=None)

@click.command()
@click.option("--port", default=3000, help="Port to listen on for HTTP")
@click.option(
    "--log-level",
    default="INFO",
    help="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
)
@click.option(
    "--json-response",
    is_flag=True,
    default=False,
    help="Enable JSON responses instead of SSE streams",
)
def main(
    port: int,
    log_level: str,
    json_response: bool,
) -> int:
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    app = Server("mcp-streamable-http-stateless")

    @app.call_tool()
    async def call_tool(
        name: str, arguments: dict
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        try:
            result = await call_api_tool(name, arguments)
            return [types.TextContent(type="text", text=str(result))]
        except ValueError as e:
            return [types.TextContent(type="text", text=str(e))]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error calling tool {name}: {str(e)}")]

    @app.list_tools()
    async def list_tools() -> list[types.Tool]:
        # 从上下文变量中获取tool_group
        tool_group = current_tool_group.get()
        print("================================================tool_group")
        print(tool_group)
        enhancedServerToolManager = EnhancedServerToolManager()
        tool_definitions = enhancedServerToolManager.get_tools_by_server(server_name=tool_group)
        return [
            types.Tool(
                name=tool["name"],
                description=tool["description"],
                inputSchema=tool["inputSchema"],
            )
            for tool in tool_definitions
        ]

    # Create the session manager with true stateless mode
    session_manager = StreamableHTTPSessionManager(
        app=app,
        event_store=None,
        json_response=json_response,
        stateless=True,
    )

    async def handle_streamable_http(
        scope: Scope, receive: Receive, send: Send
    ) -> None:
        # Extract tool_group from path if present
        path_parts = scope["path"].strip("/").split("/")
        tool_group = path_parts[1] if len(path_parts) > 1 else None
        
        # 设置当前请求的tool_group到上下文变量中
        token = current_tool_group.set(tool_group)
        try:
            await session_manager.handle_request(scope, receive, send)
        finally:
            # 清理上下文变量
            current_tool_group.reset(token)

    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette) -> AsyncIterator[None]:
        """Context manager for session manager."""
        async with session_manager.run():
            logger.info("Application started with StreamableHTTP session manager!")
            try:
                yield
            finally:
                logger.info("Application shutting down...")
    normalized_app = PathNormalizerASGIApp(handle_streamable_http)
    post_only_app = PostOnlyASGIApp(normalized_app)
    # Create an ASGI application using the transport
    starlette_app = Starlette(
        debug=True,
        routes=[
            Mount("/mcp", app=post_only_app),
        ],
        lifespan=lifespan,
    )
    import uvicorn

    uvicorn.run(starlette_app, host="127.0.0.1", port=port)

    return 0
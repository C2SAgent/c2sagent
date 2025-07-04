import contextlib
import logging
from collections.abc import AsyncIterator

import click
import mcp.types as types
from mcp.server.lowlevel import Server
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from starlette.applications import Starlette
from starlette.routing import Mount, Route
from starlette.types import Receive, Scope, Send

from src_mcp.mcp_server.manager_server_tool import EnhancedServerToolManager
from src_mcp.mcp_server.manager_tool import call_api_tool

logger = logging.getLogger(__name__)

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

    # We'll modify list_tools to accept an optional tool_group parameter
    @app.list_tools()
    async def list_tools(tool_group: str | None = None) -> list[types.Tool]:
        tool_definitions = EnhancedServerToolManager.get_tools_by_server(tool_group)
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
        
        # Store tool_group in the scope so session_manager can access it
        scope["tool_group"] = tool_group
        await session_manager.handle_request(scope, receive, send)

    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette) -> AsyncIterator[None]:
        """Context manager for session manager."""
        async with session_manager.run():
            logger.info("Application started with StreamableHTTP session manager!")
            try:
                yield
            finally:
                logger.info("Application shutting down...")

    # Create an ASGI application using the transport
    starlette_app = Starlette(
        debug=True,
        routes=[
            Mount("/mcp", app=handle_streamable_http),
            Route("/mcp/{tool_group:path}", app=handle_streamable_http),
        ],
        lifespan=lifespan,
    )

    import uvicorn

    uvicorn.run(starlette_app, host="127.0.0.1", port=port)

    return 0

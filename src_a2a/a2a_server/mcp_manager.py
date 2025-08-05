import asyncio
from pathlib import Path
from typing import AsyncGenerator
import aiohttp


async def call_mcp_client(url: str, query: str, agent_index, mcp_server_id) -> str:
    """Call an MCP Client with the given URL and query.

    Args:
        url (str): The URL of the MCP Client.
        query (str): The query to pass to the MCP Client.


    Returns:
        str: The result of the MCP Client call.
    """
    headers = {"Content-Type": "application/json"}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                headers=headers,
                json={
                    "query": query,
                    "mcp_server_id": mcp_server_id,
                    "agent_id": agent_index,
                },
            ) as response:
                result = await response.json()
                return result["data"]
    except Exception as e:
        raise e


async def call_mcp_client_streaming(
    url: str, query: str, agent_index, mcp_server_id
) -> AsyncGenerator[str, None]:
    """Call an MCP Client with streaming response, yielding chunks as they arrive."""
    headers = {"Content-Type": "application/json"}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                headers=headers,
                json={
                    "query": query,
                    "mcp_server_id": mcp_server_id,
                    "agent_id": agent_index,
                },
            ) as response:
                response.raise_for_status()

                async for chunk in response.content.iter_any():
                    yield chunk.decode("utf-8")

    except Exception as e:
        print(f"Error in streaming request: {str(e)}")
        raise


# if __name__ == '__main__':
#     print(asyncio.run(get_mcp_tool_prompt('https://gitmcp.io/google/A2A')))
#     result = asyncio.run(
#         call_mcp_tool('https://gitmcp.io/google/A2A', 'fetch_A2A_documentation')
#     )
#     for content in result.content:
#         if isinstance(content, TextContent):
#             print(content.text)

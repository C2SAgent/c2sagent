import asyncio
import json
from pathlib import Path
from typing import AsyncGenerator
import aiohttp


async def call_default_mcp() -> str:
    pass


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
    url: str, query: str, agent_index: int, mcp_server_id: int
) -> AsyncGenerator[dict, None]:
    """调用MCP客户端并流式接收响应，解析每个JSON chunk"""
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

                buffer = ""
                async for chunk_bytes in response.content.iter_any():
                    chunk_str = chunk_bytes.decode("utf-8")
                    buffer += chunk_str

                    # 按行分割处理NDJSON
                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        if line.strip():
                            try:
                                yield json.loads(line)
                            except json.JSONDecodeError as e:
                                print(f"JSON解析错误: {e}, 原始数据: {line}")
                                continue

    except Exception as e:
        print(f"流式请求错误: {str(e)}")
        raise


# if __name__ == '__main__':
#     print(asyncio.run(get_mcp_tool_prompt('https://gitmcp.io/google/A2A')))
#     result = asyncio.run(
#         call_mcp_tool('https://gitmcp.io/google/A2A', 'fetch_A2A_documentation')
#     )
#     for content in result.content:
#         if isinstance(content, TextContent):
#             print(content.text)

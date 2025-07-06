import asyncio
from pathlib import Path
import aiohttp

async def call_mcp_client(
    url: str, query: str, agent_index, mcp_server_id
) -> str:
    """Call an MCP Client with the given URL and query.

    Args:
        url (str): The URL of the MCP Client.
        query (str): The query to pass to the MCP Client.
        

    Returns:
        str: The result of the MCP Client call.
    """ 
    print("=======================================================url")
    print(url)
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                json={
                    "query": query,
                    "agent_index": agent_index,
                    "mcp_server_id": mcp_server_id
                },
            ) as response:
                return await response.json()
    except Exception as e:
        raise e



# if __name__ == '__main__':
#     print(asyncio.run(get_mcp_tool_prompt('https://gitmcp.io/google/A2A')))
#     result = asyncio.run(
#         call_mcp_tool('https://gitmcp.io/google/A2A', 'fetch_A2A_documentation')
#     )
#     for content in result.content:
#         if isinstance(content, TextContent):
#             print(content.text)


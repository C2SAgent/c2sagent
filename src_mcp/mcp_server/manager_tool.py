import aiohttp
import httpx
import logging

logger = logging.getLogger(__name__)
from tinydb import TinyDB, Query
db = TinyDB(r'project\server_tool\server_tool_life.json')
tools_table = db.table('tools')

async def get_tool_definitions():
    data = tools_table.all()
    if not data:
        return []
    return data

async def call_api_tool(name: str, arguments: dict) -> str:
    """调用API工具"""
    ToolQuery = Query()
    data = tools_table.search(ToolQuery.name == name)
    if not data:
        raise ValueError(f"Tool '{name}' not found")
    
    tool = dict(data[0])
    handler = tool["handler"]
    
    try:
        url = handler["url"]
        method = handler["method"].upper()

        if method == "GET":
            request_params = {}
            request_params["key"] = handler["key"]
            request_params.update(arguments)
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=request_params) as response:
                    return await response.json()
        
        if method == "POST":
            request_params = {}
            request_params["key"] = handler["key"]
            request_params.update(arguments)
            async with aiohttp.ClientSession() as session:
                async with session.post(url, params=request_params) as response:
                    return await response.json()
                

        raise ValueError(f"Unsupported HTTP method: {method}")
        
    except httpx.HTTPStatusError as e:
        logger.error(f"API request failed: {str(e)}")
        raise ValueError(f"API request failed: {e.response.text}")
    except Exception as e:
        logger.error(f"Tool execution error: {str(e)}")
        raise ValueError(f"Tool execution error: {str(e)}")

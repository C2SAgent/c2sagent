from fastapi import Depends
from src_mcp.mcp_client.mcp_client import ChatSession
from . import get_llm_client, get_mcp_servers
from fastmcp import FastMCP

async def get_chat_session() -> ChatSession:
    """获取聊天会话依赖项"""
    return ChatSession(
        servers=get_mcp_servers(),
        llm_client=get_llm_client()
    )

# 可复用的依赖项（供其他路由使用）
chat_session_depends = Depends(get_chat_session)
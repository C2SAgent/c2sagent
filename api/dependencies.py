from fastapi import Depends
from project.mcp_client.mcp_client_life import ChatSession
from . import get_llm_client, get_mcp_servers

async def get_chat_session() -> ChatSession:
    """获取聊天会话依赖项"""
    return ChatSession(
        servers=get_mcp_servers(),
        llm_client=get_llm_client()
    )

# 可复用的依赖项（供其他路由使用）
chat_session_depends = Depends(get_chat_session)
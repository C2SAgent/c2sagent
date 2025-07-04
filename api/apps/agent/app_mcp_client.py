from fastapi import APIRouter, Request
from api.utils.api_utils import BaseResponse
from src_mcp.mcp_client.mcp_client import ChatSession
import logging
from ...dependencies import chat_session_depends

chat_router = APIRouter(prefix="/mcp_client")

@chat_router.post(
    "/{mcp_server_id}/{agent_id}", summary="与mcp agent进行对话"
)
async def answer_with_server_code(
    request: Request,
    chat_session: ChatSession = chat_session_depends,
):
    request_data = await request.json()
    query = request_data.get('query')
    print(query)
    try:
        messages = [{"role": "user", "content": query}]
        answer = await chat_session._get_agent_response(messages, mcp_server_id, agent_id)
        result = BaseResponse(code=200, msg="success", data=answer)
        return result
    except Exception as e:
        logging.error(f"Chat request failed: {e}", exc_info=True)
        return BaseResponse(code=500, msg="请求失败")
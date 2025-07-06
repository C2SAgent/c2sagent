from fastapi import APIRouter, Body, FastAPI, Path, Request
from fastapi.responses import JSONResponse
from api.utils.api_utils import BaseResponse
from src_mcp.mcp_client import lifespan
from src_mcp.mcp_client.mcp_client import ChatSession
import logging
from src_mcp.mcp_client.dependencies import chat_session_depends

app = FastAPI()

@app.post(
    "/chat", summary="与mcp agent进行对话",
    response_model=BaseResponse,
    response_class=JSONResponse  # 确保返回JSON格式
)
async def answer_with_server_code(
    request: Request,
    query: str = Body(...),
    mcp_server_id: int = Body(..., description="MCP服务器ID"),
    agent_id: int = Body(..., description="Agent ID"),
    chat_session: ChatSession = chat_session_depends,
):
    print("=============================================answer_with_server_code")
    print(mcp_server_id)
    # request_data = await request.json()
    # query = request_data.get('query')
    print(query)
    try:
        messages = [{"role": "user", "content": query}]
        answer = await chat_session._get_agent_response(messages, mcp_server_id, agent_id)
        result = BaseResponse(code=200, msg="success", data=answer)
        return result
    except Exception as e:
        logging.error(f"Chat request failed: {e}", exc_info=True)
        return BaseResponse(code=500, msg="请求失败")
import json
from fastapi import APIRouter, Body, FastAPI, Path, Request
from fastapi.responses import JSONResponse, StreamingResponse
from api.utils.api_utils import BaseResponse
from src_mcp.mcp_client import lifespan
from src_mcp.mcp_client.mcp_client import ChatSession
import logging
from src_mcp.mcp_client.dependencies import chat_session_depends

app = FastAPI()


@app.post(
    "/ask_mcp",
    summary="与mcp agent进行对话",
    response_model=BaseResponse,
    response_class=JSONResponse,  # 确保返回JSON格式
)
async def answer_with_server_code(
    request: Request,
    query: str = Body(...),
    mcp_server_id: int = Body(..., description="MCP服务器ID"),
    agent_id: int = Body(..., description="Agent ID"),
    chat_session: ChatSession = chat_session_depends,
):
    try:
        messages = [{"role": "user", "content": query}]
        answer = await chat_session._get_agent_response(
            messages, mcp_server_id, agent_id
        )
        result = BaseResponse(code=200, msg="success", data=answer)
        return result
    except Exception as e:
        logging.error(f"Chat request failed: {e}", exc_info=True)
        return BaseResponse(code=500, msg="请求失败")


# TODO: 待完成流式mcp
@app.post(
    "/ask_mcp_streaming",
    summary="与mcp agent进行对话(流式)",
    response_class=BaseResponse,  # 改为流式响应
)
async def answer_with_server_code_streaming(
    request: Request,
    query: str = Body(...),
    mcp_server_id: int = Body(..., description="MCP服务器ID"),
    agent_id: int = Body(..., description="Agent ID"),
    chat_session: ChatSession = chat_session_depends,
):
    try:
        messages = [{"role": "user", "content": query}]
        answer = await chat_session._get_agent_response(
            messages, mcp_server_id, agent_id
        )
        result = BaseResponse(code=200, msg="success", data=answer)
        return result
    except Exception as e:
        logging.error(f"Chat request failed: {e}", exc_info=True)
        return BaseResponse(code=500, msg="请求失败")

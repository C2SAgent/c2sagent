import os
from typing import Annotated, Any, Dict
from fastapi import Body, FastAPI, Depends, HTTPException, Query, Request
from fastapi.encoders import jsonable_encoder
from api.apps.auths import auth
from api.apps.auths.dependencies import token_required
from api.utils.api_utils import BaseResponse, ListResponse
from core.db.base import DatabaseManager
from model.api_model import model_create_agent, model_create_mcp
from model import model_agent as models
from model.api_model.model_tool import Tool
from src_mcp.mcp_server.manager_server_tool import EnhancedServerToolManager
from .database import engine, get_db
from sqlalchemy.orm import Session

from api.apps.agent.config import settings

DATABASE_URL = settings.DATABASE_URL
db = DatabaseManager(DATABASE_URL)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)


app = FastAPI(on_startup=[init_db])


@app.post("/create", response_model=BaseResponse)
async def do_mcp_create(
    request: Request,
    name: str = Body(...),
    current_user: models.UserConfig = Depends(auth.get_current_active_user),
):
    await db.insert(
        models.McpServer, {"name": name, "url": "", "user_id": current_user.id}
    )

    return BaseResponse()


@app.get("/list", response_model=ListResponse)
async def do_mcp_list(
    current_user: models.UserConfig = Depends(auth.get_current_active_user),
):
    mcps = await db.fetch_all(models.McpServer, {"user_id": current_user.id})
    return {"data": jsonable_encoder(mcps)}


@app.post("/corr_tool", response_model=BaseResponse)
async def do_mcp_corr_tool(
    request=Request,
    mcp_server_id: int = Body(...),
    tool: Dict[str, Any] = Body(...),
    current_user: models.UserConfig = Depends(auth.get_current_active_user),
):
    manager = EnhancedServerToolManager()
    manager.add_tool_to_server(str(mcp_server_id), tool)

    return BaseResponse()


@app.post("/discorr_tool", response_model=BaseResponse)
async def do_mcp_discorr_tool(
    request=Request,
    mcp_server_id: int = Body(...),
    tool_name: str = Body(...),
    current_user: models.UserConfig = Depends(auth.get_current_active_user),
):
    # print(tool)
    manager = EnhancedServerToolManager()
    manager.remove_tool_from_server(str(mcp_server_id), tool_name)

    return BaseResponse()


@app.get("/tool/list", response_model=BaseResponse)
async def do_tool_list(
    request: Request,
    mcp_server_id: int = Query(...),
    current_user: models.UserConfig = Depends(auth.get_current_active_user),
):
    manager = EnhancedServerToolManager()
    tools = []
    for tool in manager.get_tools_by_server(str(mcp_server_id)):
        tools.append(tool)
    return ListResponse(data=tools)

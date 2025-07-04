from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException
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

db = DatabaseManager('postgresql://postgres:postgre@localhost/manager_agent')

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/create", response_model=BaseResponse)
@token_required
async def do_mcp_create(
    mcp_server: model_create_mcp.McpServer,
):
    current_user: Annotated[models.UserConfig, Depends(auth.get_current_active_user)]
    
    db.insert(models.McpServer, {
        "name": mcp_server.name,
        "user_id": current_user.id
    })

    return BaseResponse()

@app.post("/list", response_model=ListResponse)
@token_required
async def do_mcp_list():
    current_user: Annotated[models.UserConfig, Depends(auth.get_current_active_user)]
    
    mcps = db.fetch_all(models.McpServer, {"user_id": current_user.id})
    
    return ListResponse(data=mcps)

@app.post("/corr_tool", response_model=BaseResponse)
@token_required
async def do_mcp_corr_tool(
    mcp_server: model_create_mcp.McpServer,
    tool: Tool,
):
    manager = EnhancedServerToolManager()
    manager.add_tool_to_server(str(mcp_server.id), tool)
    
    return BaseResponse()

@app.post("/tool/list", response_model=BaseResponse)
@token_required
async def do_tool_list(mcp_server: model_create_mcp.McpServer):
    manager = EnhancedServerToolManager()
    tools = []
    for tool in manager.get_tools_by_server(mcp_server.id):
        tools.append(tool)
    
    return ListResponse(data=tools)


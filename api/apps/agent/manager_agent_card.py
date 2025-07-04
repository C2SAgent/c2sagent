from typing import Annotated

from fastapi import Body, FastAPI, Depends, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from api.apps.auths import auth
from api.apps.auths.dependencies import token_required
from api.utils.api_utils import BaseResponse, ListResponse
from core.db.base import DatabaseManager
from model.api_model import model_create_agent
from model import model_agent as models
from .database import engine, get_db
from sqlalchemy.orm import Session

db = DatabaseManager('postgresql://postgres:postgre@localhost/manager_agent')

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/create", response_model=BaseResponse)
async def do_agent_create(
    request: Request,
    name: str = Body(...),
    description: str = Body(""),

    llm_name: str = Body(""),
    llm_url: str = Body(""),
    llm_key: str = Body(""),
    
    version: str = Body("1.0.0"),
    streaming: bool = Body(False),
    examples: list[str] = Body([]),
    
    current_user: models.UserConfig = Depends(auth.get_current_active_user)
): 
    db.insert(models.AgentCard, {
        "name": name,
        "description": description,
        "version": version,
        "streaming": streaming,
        "examples": examples,
        "user_id": current_user.id,

        "llm_name": llm_name,
        "llm_url": llm_url,
        "llm_key": llm_key
    })
    return BaseResponse()

@app.get("/list", response_model=ListResponse)
async def do_agent_list(
    current_user: Annotated[models.UserConfig, Depends(auth.get_current_active_user)]
):
    agents = db.fetch_all(models.AgentCard, {"user_id": current_user.id})
    return {"data": jsonable_encoder(agents)}

@app.post("/delete", response_model=BaseResponse)
async def do_agent_delete(
    request: Request,
    id: int = Body(...),
    current_user: models.UserConfig = Depends(auth.get_current_active_user)
):
    db.delete(models.AgentCard, id=id, user_id=current_user.id)
    return BaseResponse()

@app.post("/corr_mcp", response_model=BaseResponse)
async def do_agent_corr_mcp(
    agent_card: model_create_agent.AgentCard,
    mcp_server: model_create_agent.McpServer,
):
    db.insert(models.AgentCardAndMcpServer, {
        "agent_card_id": agent_card.id,
        "mcp_server_id": mcp_server.id
    })
    return BaseResponse()


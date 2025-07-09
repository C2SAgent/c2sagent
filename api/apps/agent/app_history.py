import json
from fastapi import Body, FastAPI, HTTPException, Query, Request, Depends
from pydantic import BaseModel
from typing import Literal, Optional
import asyncio
from src_a2a.a2a_client.agent import Agent
from api.apps.auths import auth
from api.utils.api_utils import BaseResponse, ListResponse
from core.db.base import DatabaseManager
from model.model_agent import AgentCard
from model import model_agent as models
from fastapi.responses import StreamingResponse

app = FastAPI()
db = DatabaseManager("postgresql://postgres:postgre@localhost/manager_agent")

@app.post("/history_message", response_model=ListResponse)
async def ask_agent(
    request: Request,
    id: int = Body(..., "历史消息id"),
    current_user: models.UserConfig = Depends(auth.get_current_active_user)
):
    """Endpoint to interact with the Agent.
    
    Args:
        request (AgentRequest): Contains all the parameters needed to query the agent.
        
    Returns:
        AgentResponse: The response from the agent.
    """
    
    
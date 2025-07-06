from fastapi import FastAPI, HTTPException, Query, Request, Depends
from pydantic import BaseModel
from typing import Literal, Optional
import asyncio
from src_a2a.a2a_client.agent import Agent
from api.apps.auths import auth
from api.utils.api_utils import BaseResponse
from core.db.base import DatabaseManager
from model.model_agent import AgentCard
from model import model_agent as models

app = FastAPI()
db = DatabaseManager("postgresql://postgres:postgre@localhost/manager_agent")

class AgentRequest(BaseModel):
    host: str = 'localhost'
    port: int = 10001
    mode: Literal['completion', 'streaming'] = 'streaming'
    user_id: str
    question: str

class AgentResponse(BaseModel):
    result: str

@app.get("/ask-agent", response_model=BaseResponse)
async def ask_agent(
    request: Request,
    question: str = Query(...)
    # current_user: models.UserConfig = Depends(auth.get_current_active_user)
):
    """Endpoint to interact with the Agent.
    
    Args:
        request (AgentRequest): Contains all the parameters needed to query the agent.
        
    Returns:
        AgentResponse: The response from the agent.
    """
    
    print(question)
    agent_finds = db.fetch_all(AgentCard, {"user_id": 36})
    if not agent_finds:
        raise HTTPException(status_code=404, detail="Agent not found for this user")

    agent = Agent(
        mode="complete",
        token_stream_callback=None,
        agent_urls=[
            f'http://localhost:10001/a2a/{agent_find.id}'
            for agent_find in agent_finds
        ],
        user_id=36
    )

    result = await agent.stream(question)


    return BaseResponse(data=result)
    
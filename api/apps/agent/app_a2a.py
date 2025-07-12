from datetime import datetime
import json
from fastapi import FastAPI, HTTPException, Query, Request, Depends
from pydantic import BaseModel
from typing import Literal, Optional
import asyncio
from core.db.base_mongo import MongoDBManager
from src_a2a.a2a_client.agent import Agent
from api.apps.auths import auth
from api.utils.api_utils import BaseResponse
from core.db.base import DatabaseManager
from model.model_agent import AgentCard
from model import model_agent as models
from fastapi.responses import StreamingResponse

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

@app.get("/ask_a2a", response_model=BaseResponse)
async def ask_agent(
    request: Request,
    question: str = Query(...),
    session_id: str = Query(''),
    current_user: models.UserConfig = Depends(auth.get_current_active_user)
):
    """Endpoint to interact with the Agent.
    
    Args:
        request (AgentRequest): Contains all the parameters needed to query the agent.
        
    Returns:
        AgentResponse: The response from the agent.
    """
    mongo = MongoDBManager()
    try:
        mongo.connect()
        question_msg = {
            "role": "user",
            "content": question,
            "timestamp": datetime.now().isoformat()
        }
        if session_id == '':
            session_id = mongo.create_session(str(current_user.id), question_msg)
        else:
            mongo.add_message(session_id, question_msg)
        print("===========================session_id")
        print(session_id)
        messages = mongo.get_session_by_ids(str(current_user.id), session_id)['messages']
        
        agent_finds = db.fetch_all(AgentCard, {"user_id": current_user.id})
        if not agent_finds:
            raise HTTPException(status_code=404, detail="Agent not found for this user")

        agent = Agent(
            mode="complete",
            token_stream_callback=None,
            agent_urls=[
                f'http://localhost:10001/a2a/{agent_find.id}'
                for agent_find in agent_finds
            ],
            user_id=current_user.id
        )

        result = await agent.completion(messages)
        message_result = {
            "role": "system",
            "content": result[0]["answer"],
            "timestamp": datetime.now().isoformat()
        }
        mongo.add_message(session_id, message_result)
    finally:
        mongo.close()

    return BaseResponse(data=result[0]["answer"])

@app.get("/ask_a2a_streaming", response_model=BaseResponse)
async def ask_agent_streaming(
    request: Request,
    question: str = Query(...),
    current_user: models.UserConfig = Depends(auth.get_current_active_user)
):
    """Endpoint to interact with the Agent.
    
    Args:
        request (AgentRequest): Contains all the parameters needed to query the agent.
        
    Returns:
        AgentResponse: The response from the agent.
    """
    
    agent_finds = db.fetch_all(AgentCard, {"user_id": 36})
    if not agent_finds:
        raise HTTPException(status_code=404, detail="Agent not found for this user")

    agent = Agent(
        mode="steaming",
        token_stream_callback=None,
        agent_urls=[
            f'http://localhost:10001/a2a/{agent_find.id}'
            for agent_find in agent_finds
        ],
        user_id=36
    )

    async def generate_stream():
        async for chunk in agent.streaming(question):
            # Format each chunk as a Server-Sent Event
            yield f"data: {json.dumps({'data': chunk})}\n\n"
            
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )
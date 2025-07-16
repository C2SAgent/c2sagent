from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Literal, Optional
import asyncio
from agent import Agent
from core.db.base import DatabaseManager
from model.model_agent import AgentCard

app = FastAPI()
DATABASE_URL = os.getenv("DATABASE_URL")
db = DatabaseManager(DATABASE_URL)


class AgentRequest(BaseModel):
    host: str = 'localhost'
    port: int = 10001
    mode: Literal['completion', 'streaming'] = 'streaming'
    user_id: str
    question: str

class AgentResponse(BaseModel):
    result: str

@app.post("/ask-agent", response_model=AgentResponse)
async def ask_agent(request: AgentRequest):
    """Endpoint to interact with the Agent.
    
    Args:
        request (AgentRequest): Contains all the parameters needed to query the agent.
        
    Returns:
        AgentResponse: The response from the agent.
    """
    try:
        agent_find = db.fetch_all(AgentCard, {"user_id": request.user_id})
        if not agent_find:
            raise HTTPException(status_code=404, detail="Agent not found for this user")

        agent = Agent(
            mode=request.mode,
            token_stream_callback=None,
            agent_urls=[
                f'http://{request.host}:{request.port}/{agent_index}'
                for agent_index in agent_find.id
            ],
            user_id=request.user_id
        )

        if request.mode == 'streaming':
            result = await agent.stream(request.question)
        else:
            result = await agent.complete(request.question)

        return AgentResponse(result=result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class AgentCard(BaseModel):
    id: int
    name: str
    description: str
    version: str
    streaming: bool
    examples: list[str]

    llm_name: str
    llm_url: str
    llm_key: str

class McpServer(BaseModel):
    id: int
    name: str

class AgentCardAndMcpServer(BaseModel):
    agent_card_id: int
    mcp_server_id: int

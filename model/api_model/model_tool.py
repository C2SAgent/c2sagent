from pydantic import BaseModel
from typing import List, Optional, Dict

class ToolInputSchema(BaseModel):
    type: str
    properties: dict
    required: List[str]

class ToolHandler(BaseModel):
    type: str
    url: str
    method: str
    key: str

class Tool(BaseModel):
    name: str
    description: str
    inputSchema: ToolInputSchema
    handler: ToolHandler

class ToolUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    inputSchema: Optional[ToolInputSchema] = None
    handler: Optional[ToolHandler] = None

class DeleteToolRequest(BaseModel):
    name: str
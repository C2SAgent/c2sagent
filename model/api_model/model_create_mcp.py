from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class McpServer(BaseModel):
    id: str
    name: str

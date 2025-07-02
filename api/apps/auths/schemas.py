from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserBase(BaseModel):
    name: str
    core_llm_name: Optional[str] = None
    core_llm_url: Optional[str] = None
    core_llm_key: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    id: int
    # is_active: bool
    # is_superuser: bool

    # class Config:
    #     orm_mode = True

class UserLogin(BaseModel):
    name: str
    password: str
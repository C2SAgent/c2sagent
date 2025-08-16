import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from datetime import datetime
import io
import json
import os
import re
from fastapi import (
    Body,
    FastAPI,
    File,
    Form,
    HTTPException,
    Query,
    Request,
    Depends,
    UploadFile,
)
import pandas as pd
from pydantic import BaseModel
from typing import Literal, Optional
import asyncio
from core.db.base_mongo import MongoDBManager
from core.oss.base_oss import OSSManager
from src_a2a.a2a_client.agent import Agent
from api.apps.auths import auth
from api.utils.api_utils import BaseResponse
from core.db.base import DatabaseManager
from core.llm.llm_client import LLMClient
from model.model_agent import AgentCard, UserConfig
from model import model_agent as models
from fastapi.responses import StreamingResponse
from fastapi import UploadFile, Form
from datetime import datetime
from fastapi.encoders import jsonable_encoder
import re
import json
import pandas as pd
import uuid


from api.apps.agent.config import settings

from api.apps.agent.database import engine

from core.timeseries.time_gpt import TimeGPT

DATABASE_URL = settings.DATABASE_URL
db = DatabaseManager(DATABASE_URL)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)


app = FastAPI(on_startup=[init_db])


@app.get("/list", response_model=BaseResponse)
async def do_media_list(
    request: Request,
    current_user: models.UserConfig = Depends(auth.get_current_active_user),
):
    medias = await db.fetch_all(models.UserAndMedia, {"user_id": current_user.id})
    return {"data": jsonable_encoder(medias)}


@app.post("/update", response_model=BaseResponse)
async def do_media_update(
    request: Request,
    name: str = Body(...),
    jct: str = Body(...),
    sessdata: str = Body(...),
    current_user: models.UserConfig = Depends(auth.get_current_active_user),
):
    await db.update(
        models.UserAndMedia,
        {"user_id": current_user.id, "name": name, "jct": jct, "sessdata": sessdata},
    )
    return BaseResponse()

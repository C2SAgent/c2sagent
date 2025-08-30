import sys
from pathlib import Path

from service.apps.agent.app_a2a import App_A2A

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
import re
import json
import pandas as pd
import uuid


from api.apps.agent.config import settings

from api.apps.agent.database import engine

from core.timeseries.time_gpt import TimeGPT

DATABASE_URL = settings.DATABASE_URL
db = DatabaseManager(DATABASE_URL)

# 常量定义
FORECAST_PATH_PREFIX = "forecasts"
CSV_CONTENT_TYPE = "text/csv"
PNG_CONTENT_TYPE = "image/png"


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)


app = FastAPI(on_startup=[init_db])


@app.get("/ask_a2a", response_model=BaseResponse)
async def ask_agent(
    request: Request,
    question: str = Query(...),
    session_id: str = Query(""),
    current_user: models.UserConfig = Depends(auth.get_current_active_user),
):
    """Endpoint to interact with the Agent.

    Args:
        request (AgentRequest): Contains all the parameters needed to query the agent.

    Returns:
        AgentResponse: The response from the agent.
    """
    mongo = MongoDBManager()
    try:
        await mongo.connect()
        question_msg = {
            "role": "user",
            "content": question,
            "timestamp": datetime.now().isoformat(),
        }
        if session_id == "":
            session_id = await mongo.create_session(str(current_user.id), question_msg)
        else:
            await mongo.add_message(session_id, question_msg)

        messages_find = await mongo.get_session_by_ids(str(current_user.id), session_id)
        messages = messages_find["messages"]

        agent_finds = await db.fetch_all(AgentCard, {"user_id": current_user.id})
        if not agent_finds:
            raise HTTPException(status_code=404, detail="Agent not found for this user")

        agent = Agent(
            mode="complete",
            token_stream_callback=None,
            agent_urls=[
                f"http://localhost:10001/a2a/{agent_find.id}"
                for agent_find in agent_finds
            ],
            user_id=current_user.id,
        )

        result = await agent.completion(messages)

        message_result = {
            "role": "system",
            "content": result,
            "timestamp": datetime.now().isoformat(),
        }
        await mongo.add_message(session_id, message_result)
    finally:
        await mongo.close()

    return BaseResponse(data=result)


@app.post("/ask_a2a_streaming")
async def stream_ask_a2a(
    request: Request,
    question: str = Form(...),
    session_id: str = Form(...),
    isTimeSeries: bool = Form(False),
    isAgent: bool = Form(False),
    isThought: bool = Form(False),
    isDocAnalysis: bool = Form(False),
    files: UploadFile = File(None),
    current_user: models.UserConfig = Depends(auth.get_current_active_user),
):


    if files and files.content_type == CSV_CONTENT_TYPE:
        oss = OSSManager()
        input_data_url = None
        temp_content = await files.read()
        object_name = f"{FORECAST_PATH_PREFIX}/{session_id}/{datetime.now().isoformat()}_{uuid.uuid4()}.csv"
        input_data_url = oss.upload_object(
            bucket_name="c2sagent",
            object_name=object_name,
            content=temp_content,
        )

    mongo = MongoDBManager()
    user_find = await db.fetch_one(UserConfig, id=current_user.id)
    core_llm_name = user_find.core_llm_name
    core_llm_url = user_find.core_llm_url
    core_llm_key = user_find.core_llm_key
    llm_client = LLMClient(core_llm_url, core_llm_key)

    async def event_stream():
        await mongo.connect()
        try:
            nonlocal session_id

            agent_finds = await db.fetch_all(AgentCard, {"user_id": current_user.id})
            if not agent_finds:
                raise HTTPException(
                    status_code=404, detail="Agent not found for this user"
                )
            agent = Agent(
                mode="complete",
                token_stream_callback=None,
                agent_urls=[
                    f"http://localhost:10001/a2a/{agent_find.id}"
                    for agent_find in agent_finds
                ],
                user_id=current_user.id,
            )

            # History Messages
            messages_find = await mongo.get_session_by_ids(
                str(current_user.id), session_id
            )
            messages = messages_find["messages"]

            await App_A2A.save_message(question, mongo, current_user.id, session_id)

            # 时序预测处理
            if isTimeSeries and input_data_url:
                try:
                    async for result in App_A2A.do_timeseries_forecast(
                        input_data_url,
                        current_user.id,
                        question,
                        llm_client,
                        core_llm_url,
                        core_llm_key,
                        oss,
                        session_id,
                        FORECAST_PATH_PREFIX,
                        mongo,
                        agent,
                    ):
                        yield result

                except Exception as e:
                    yield json.dumps({"event": "error", "data": str(e)}) + "\n\n"

            elif isAgent:
                agent_finds = await db.fetch_all(AgentCard, {"user_id": current_user.id})
                if not agent_finds:
                    raise HTTPException(
                        status_code=404, detail="Agent not found for this user"
                    )
                agent = Agent(
                    mode="complete",
                    token_stream_callback=None,
                    agent_urls=[
                        f"http://localhost:10001/a2a/{agent_find.id}"
                        for agent_find in agent_finds
                    ],
                    user_id=current_user.id,
                )
                async for result in App_A2A.do_multi_agent(
                    agent,
                    messages,
                    question,
                    current_user.id,
                    session_id,
                    mongo,
                    llm_client,
                    core_llm_name,
                    core_llm_url,
                    core_llm_key,
                ):
                    yield result

            elif isThought:
                async for result in App_A2A.do_llm_thought(
                    mongo,
                    current_user.id,
                    session_id,
                    llm_client,
                    core_llm_name,
                    core_llm_url,
                    core_llm_key,
                ):
                    yield result

            else:
                async for result in App_A2A.do_llm(
                    mongo,
                    current_user.id,
                    session_id,
                    llm_client,
                    core_llm_name,
                    core_llm_url,
                    core_llm_key,
                ):
                    yield result

        except Exception as e:
            yield json.dumps({"event": "error", "data": str(e)}) + "\n\n"
        finally:
            await mongo.close()

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )

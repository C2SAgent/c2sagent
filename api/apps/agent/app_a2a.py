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
    isDocAnalysis: bool = Form(False),
    files: UploadFile = File(None),
    current_user: models.UserConfig = Depends(auth.get_current_active_user),
):
    oss = OSSManager()
    input_data_url = None

    if files and files.content_type == CSV_CONTENT_TYPE:
        temp_content = await files.read()
        object_name = f"{FORECAST_PATH_PREFIX}/{session_id}/{datetime.now().isoformat()}_{uuid.uuid4()}.csv"
        input_data_url = oss.upload_object(
            bucket_name="c2sagent",
            object_name=object_name,
            content=temp_content,
        )

    mongo = MongoDBManager()
    user_find = await db.fetch_one(UserConfig, id=current_user.id)
    core_llm_url = user_find.core_llm_url
    core_llm_key = user_find.core_llm_key
    llm_client = LLMClient(core_llm_url, core_llm_key)

    async def event_stream():
        await mongo.connect()
        try:
            predictor = TimeGPT()
            messages_find = await mongo.get_session_by_ids(
                str(current_user.id), session_id
            )
            messages = messages_find["messages"]
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

            # 存储用户问题
            question_msg = {
                "role": "user",
                "content": question,
                "type": "text",
                "timestamp": datetime.now().isoformat(),
            }

            if not session_id:
                session_id = await mongo.create_session(current_user.id, question_msg)
            else:
                await mongo.add_message(session_id, question_msg)

            # 时序预测处理
            if isTimeSeries and input_data_url:
                try:
                    df = pd.read_csv(input_data_url)
                    if df.empty:
                        raise ValueError("Uploaded CSV file is empty.")

                    message_user = [
                        {
                            "role": "system",
                            "content": f"数据框头部为：{df.head().to_string()}\n"
                            "请对上述进行意图分析返回一个dict封装的格式示例如下："
                            '{"h"=12, "time_col"="date", "target_col"="OT"}'
                            "其中h为预测长度，必须为整型；time_col为表示时间列的头；target_col是用户所需要预测的那一列标识。"
                            "其中封装的dict必须是纯净的，不允许有任何注释或其他不相关内容"
                            "如果数据框头部中没有date和OT，那么请找出最合理的符合date和OT的列，并修改dict中的time_col和target_col的值为对应的列名，如果没有符合OT的列，那么选择最后一列作为target_col"
                            "如果没有数据框头，默认第一列头标识为time_col，第二列头标识为target_col",
                        },
                        {"role": "user", "content": question},
                    ]
                    params_response = await llm_client.get_response(
                        messages=message_user
                    )
                    match_params = re.search(r"({.*?})", params_response, re.DOTALL)
                    if not match_params:
                        raise ValueError("Failed to parse LLM response for parameters.")

                    params = json.loads(match_params.group(1).strip())
                    h = params.get("h", 12)
                    time_col = params.get("time_col", "date")
                    target_col = params.get("target_col", "OT")

                    time_fcst_df, fig_data = predictor.predict(
                        df=df, h=h, time_col=time_col, target_col=target_col
                    )

                    # 上传预测数据
                    forecast_csv = time_fcst_df.to_csv(index=False)
                    data_url = oss.upload_object(
                        bucket_name="c2sagent",
                        object_name=f"{FORECAST_PATH_PREFIX}/{session_id}/{datetime.now().isoformat()}_{uuid.uuid4()}.csv",
                        content=forecast_csv,
                    )

                    # 上传图表
                    img_url = oss.upload_object(
                        bucket_name="c2sagent",
                        object_name=f"{FORECAST_PATH_PREFIX}/{session_id}/{datetime.now().isoformat()}_{uuid.uuid4()}.png",
                        content=fig_data,
                        content_type=PNG_CONTENT_TYPE,
                    )

                    # 存储消息
                    data_message = {
                        "role": "system",
                        "content": data_url,
                        "type": "doc",
                        "timestamp": datetime.now().isoformat(),
                    }
                    await mongo.add_message(session_id, data_message)

                    img_message = {
                        "role": "system",
                        "content": img_url,
                        "type": "img",
                        "timestamp": datetime.now().isoformat(),
                    }
                    await mongo.add_message(session_id, img_message)

                    yield json.dumps({"event": "doc", "data": data_url}) + "\n\n"
                    yield json.dumps({"event": "img", "data": img_url}) + "\n\n"

                    # 分析结果
                    analysis_result = await agent.completion(
                        f"这是预测结果：\n{time_fcst_df}\n"
                        + f"这是输入数据的最后几条结果：\n{df[-24:]}\n"
                        + "请对上面的数据做出完整的分析报告，大约150字"
                    )

                    analysis_message = {
                        "role": "system",
                        "content": analysis_result,
                        "type": "text",
                        "timestamp": datetime.now().isoformat(),
                        "references": [data_url, img_url],
                    }
                    await mongo.add_message(session_id, analysis_message)

                    yield json.dumps(
                        {"event": "text", "data": analysis_result}
                    ) + "\n\n"

                except Exception as e:
                    yield json.dumps({"event": "error", "data": str(e)}) + "\n\n"

            else:
                result = await agent.completion(
                    f"这是用户的id: \n{current_user.id}\n"
                    + f"这是历史对话消息：\n{messages}\n"
                    + f"这是用户的当前消息：\n{question}\n"
                    + "如果历史信息没有用处，以及用户没有明确意图时，您只需要正常回答即可"
                )

                message = {
                    "role": "system",
                    "content": result,
                    "type": "text",
                    "timestamp": datetime.now().isoformat(),
                }

                await mongo.add_message(session_id, message)
                yield json.dumps({"event": "text", "data": result}) + "\n\n"

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

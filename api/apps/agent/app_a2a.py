from datetime import datetime
import io
import json
import os
import re
from fastapi import Body, FastAPI, File, Form, HTTPException, Query, Request, Depends, UploadFile
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

from api.apps.agent.config import settings

from .database import engine

from core.timeseries.time_gpt import TimeGPT

DATABASE_URL = settings.DATABASE_URL
db = DatabaseManager(DATABASE_URL)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

app = FastAPI(on_startup=[init_db])


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
        await mongo.connect()
        question_msg = {
            "role": "user",
            "content": question,
            "timestamp": datetime.now().isoformat()
        }
        if session_id == '':
            session_id = await mongo.create_session(str(current_user.id), question_msg)
        else:
            await mongo.add_message(session_id, question_msg)

        messages_find = await mongo.get_session_by_ids(str(current_user.id), session_id)
        messages = messages_find['messages']
        
        agent_finds = await db.fetch_all(AgentCard, {"user_id": current_user.id})
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
            "content": result,
            "timestamp": datetime.now().isoformat()
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
    # files: str = Body(""),
    files: UploadFile = File(None),
    current_user: models.UserConfig = Depends(auth.get_current_active_user)
):
    oss = OSSManager()
    if files:
        temp_content = await files.read()
        input_data_url = oss.upload_object(
            bucket_name="c2sagent",
            object_name=f"forecasts/{session_id}/{datetime.now().isoformat()}.csv",
            content=temp_content
        )
    mongo = MongoDBManager()
    user_find = await db.fetch_one(UserConfig, id = current_user.id)
    core_llm_url = user_find.core_llm_url
    core_llm_key = user_find.core_llm_key
    llm_client = LLMClient(core_llm_url, core_llm_key)
    async def event_stream():
        
        await mongo.connect()
        
        predictor = TimeGPT()
        nonlocal session_id
        messages_find = await mongo.get_session_by_ids(str(current_user.id), session_id)
        messages = messages_find['messages']
        await mongo.close()
        # print(messages)
        agent_finds = await db.fetch_all(AgentCard, {"user_id": current_user.id})
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

        try:
            # 1. 存储用户问题 
            question_msg = {
                "role": "user",
                "content": question,
                "type": "text",
                "timestamp": datetime.now().isoformat()
            }
            
            await mongo.connect()
            
            if not session_id:
                session_id = await mongo.create_session(current_user.id, question_msg)
            else:
                await mongo.add_message(session_id, question_msg)

            # 3. 时序预测处理
            if isTimeSeries and files:

                try:
                    
                    df = pd.read_csv(input_data_url)
                    
                    print("===========================================执行到了时序预测")
                    message_user = [{"role": "user", "content": f"数据框头部为：{df.head().to_string()}\n"
                                                           "请对上述进行意图分析返回一个dict封装的格式示例如下："
                                                           "{\"h\"=12, \"time_col\"=\"date\", \"target_col\"=\"OT\"}"
                                                           "其中h为预测长度，必须为整型；time_col为表示时间列的头；target_col是用户所需要预测的那一列标识。"
                                                           "其中封装的dict必须是纯净的，不允许有任何注释或其他不相关内容"},
                                    {"role": "user", "content": question}]
                    print(message_user)
                    params_response = await llm_client.get_response(messages=message_user)
                    print("========================================params_response")
                    print(params_response)
                    match_params = re.search(r"({.*?})", params_response, re.DOTALL)
                    print("========================================params")
                    print(match_params.group(1).strip())
                    params = json.loads(match_params.group(1).strip())
                    print("========================================params_json")
                    print(params)
                    h = params.get("h", 12)
                    time_col = params.get("time_col", "date")
                    target_col = params.get("target_col", "OT")
                    
                    # 执行预测
                    time_fcst_df, fig_data = predictor.predict(
                        df=df,
                        h=h,
                        time_col=time_col,
                        target_col=target_col
                    )
                    
                    # 存储预测数据到OSS
                    forecast_csv = time_fcst_df.to_csv(index=False)
                    data_url = oss.upload_object(
                        bucket_name="c2sagent",
                        object_name=f"forecasts/{session_id}/{datetime.now().isoformat()}.csv",
                        content=forecast_csv
                    )
        
                    # 存储图表数据到OSS
                    img_url = oss.upload_object(
                        bucket_name="c2sagent",
                        object_name=f"forecasts/{session_id}/{datetime.now().isoformat()}.png",
                        content=fig_data
                    )
                    
                    # 存储数据消息到MongoDB
                    data_message = {
                        "role": "system",
                        "content": data_url,
                        "type": "doc",
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    await mongo.add_message(session_id, data_message)
                    
                    # 存储图片消息到MongoDB
                    img_message = {
                        "role": "system",
                        "content": img_url,
                        "type": "img",
                        "timestamp": datetime.now().isoformat()
                    }
                    await mongo.add_message(session_id, img_message)
                    
                    yield json.dumps({
                        "event": "doc",
                        "data": data_url
                    }) + "\n\n"
                    yield json.dumps({
                        "event": "img",
                        "data": img_url
                    }) + "\n\n" 
                    # 生成分析结果

                    analysis_result = await agent.completion(f"这是预测结果：\n{time_fcst_df}\n" + f"这是输入数据的最后几条结果：\n{df[-24:]}\n" + "请对上面的数据做出完整的分析报告，大约150字")
                    # 存储分析结果到MongoDB
                    analysis_message = {
                        "role": "system",
                        "content": analysis_result,
                        "type": "text",
                        "timestamp": datetime.now().isoformat(),
                        "references": [data_url, img_url]
                    }
                    
                    await mongo.add_message(session_id, analysis_message)
                    
                    # 第二次推送：分析结果
                    yield json.dumps({
                        "event": "text",
                        "data": analysis_result
                    })+ "\n\n"
                    
                except Exception as e:
                    yield json.dumps({
                        "event": "error",
                        "data": "error"
                    }) + "\n\n"
            
            # 4. 其他处理逻辑...
            else:
                print("==============================================进行了其他逻辑处理")
                # print(messages)
                result = await agent.completion(f"这是历史对话消息：\n{messages}\n" + f"这是用户的当前消息：\n{question}\n" + "如果历史信息没有用处，以及用户没有明确意图时，您只需要正常回答即可")
                print(result)
                print("==============================================进行了其他逻辑处理完成")
                message = {
                    "role": "system",
                    "content": result,
                    "type": "text",
                    "timestamp": datetime.now().isoformat()
                }
                
                await mongo.add_message(session_id, message)

                yield json.dumps({
                    "event": "text",
                    "data": result
                })+ "\n\n"
                
        except Exception as e:
            yield json.dumps({
                "event": "error",
                "data": "error"
            }) + "\n\n"
        finally:
            await mongo.close()

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # 禁用Nginx缓冲
        }
    )
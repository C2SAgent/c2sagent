import asyncio
from datetime import datetime
import json
import re
from typing import AsyncGenerator
import uuid

import pandas as pd

from core.db.base_mongo import MongoDBManager
from core.llm.llm_client import LLMClient
from core.oss.base_oss import OSSManager
from core.timeseries.time_gpt import TimeGPT
from src_a2a.a2a_client.agent import Agent


class App_A2A:
    @staticmethod
    async def save_message(
        question: str,
        mongo: MongoDBManager,
        current_user_id: int,
        session_id: str,
    ):
        question_msg = {
            "role": "user",
            "content": question,
            "type": "text",
            "timestamp": datetime.now().isoformat(),
        }

        if not session_id:
            session_id = await mongo.create_session(current_user_id, question_msg)
        else:
            await mongo.add_message(session_id, question_msg)

    @staticmethod
    async def do_timeseries_forecast(
        input_data_url: str,
        current_user_id: int,
        question: str,
        llm_client: LLMClient,
        core_llm_url: str,
        core_llm_key: str,
        oss: OSSManager,
        session_id: str,
        FORECAST_PATH_PREFIX: str,
        mongo: MongoDBManager,
        agent: Agent,
    ):
        """
        处理预测数据流程的完整函数

        参数:
            input_data_url: 输入数据的URL
            question: 用户问题
            llm_client: LLM客户端
            core_llm_url: 核心LLM URL
            core_llm_key: 核心LLM密钥
            predictor: 预测器对象
            oss: OSS存储对象
            session_id: 会话ID
            FORECAST_PATH_PREFIX: 预测路径前缀
            mongo: MongoDB客户端
            agent: 分析代理

        返回:
            生成器，产生不同事件的数据流
        """
        # 读取数据
        predictor = TimeGPT()
        df = pd.read_csv(input_data_url)
        if df.empty:
            raise ValueError("Uploaded CSV file is empty.")

        # 构建LLM消息获取参数
        message_user = [
            {
                "role": "system",
                "content": f"数据框头部为：{df.head().to_string()}\n"
                "请对上述进行意图分析返回一个dict封装的格式示例如下："
                '{"h": 12, "time_col": "date", "target_col": "OT"}'
                "其中h为预测长度，必须为整型；time_col为表示时间列的头；target_col是用户所需要预测的那一列标识。"
                "其中封装的dict必须是纯净的，不允许有任何注释或其他不相关内容"
                "如果数据框头部中没有date和OT，那么请找出最合理的符合date和OT的列，并修改dict中的time_col和target_col的值为对应的列名，如果没有符合OT的列，那么选择最后一列作为target_col"
                "如果没有数据框头，默认第一列头标识为time_col，第二列头标识为target_col",
            },
            {"role": "user", "content": question},
        ]

        # 获取LLM响应
        params_response = ""
        async for chunk in llm_client.get_stream_com_response(
            messages=message_user,
            llm_url=core_llm_url,
            api_key=core_llm_key,
        ):
            yield json.dumps({"event": "thought", "data": chunk}) + "\n\n"
            params_response = chunk

        # 解析参数
        match_params = re.search(r"({.*?})", params_response, re.DOTALL)
        if not match_params:
            raise ValueError("Failed to parse LLM response for parameters.")

        params = json.loads(match_params.group(1).strip())
        h = params.get("h", 12)
        time_col = params.get("time_col", "date")
        target_col = params.get("target_col", "OT")

        # 进行预测
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
        question_message = f"""
            这是预测结果：\n{time_fcst_df}\n
            这是输入数据的最后几条结果：\n{df[-24:]}\n
            请对上面的数据做出完整的分析报告，大约150字
        """
        analysis_thought = ""
        analysis_text = ""
        async for result in agent.completion(question_message):
            if result["type"] == "thought":
                analysis_thought += result["content"]
                yield json.dumps(
                    {"event": "thought", "data": result["content"]}
                ) + "\n\n"
            if result["type"] == "text":
                analysis_text += result["content"]
                yield json.dumps({"event": "text", "data": result["content"]}) + "\n\n"

        # 存储分析结果
        thought_message = {
            "role": "system",
            "content": analysis_thought,
            "type": "thought",
            "timestamp": datetime.now().isoformat(),
            "references": [data_url, img_url],
        }
        await mongo.add_message(session_id, thought_message)

        analysis_message = {
            "role": "system",
            "content": analysis_text,
            "type": "text",
            "timestamp": datetime.now().isoformat(),
            "references": [data_url, img_url],
        }
        await mongo.add_message(session_id, analysis_message)

        asyncio.create_task(
            App_A2A.update_session_title(
                current_user_id,
                session_id,
                llm_client,
                core_llm_url,
                core_llm_key,
                mongo,
            )
        )

    @staticmethod
    async def update_session_title(
        current_user_id: str,
        session_id: int,
        llm_client: LLMClient,
        llm_name: str,
        llm_url: str,
        llm_key: str,
        mongo: MongoDBManager,
    ) -> None:
        await mongo.connect()
        try:
            # 1. 获取消息
            messages_find = await mongo.get_session_by_ids(
                str(current_user_id), session_id
            )
            messages = messages_find["messages"]

            # 2. 生成摘要
            abstract_title = await App_A2A.do_abstract(
                messages, llm_client, llm_name, llm_url, llm_key
            )

            # 3. 更新标题
            await mongo.update_title(session_id, abstract_title)
        except Exception as e:
            # 错误处理（可选：记录日志、重试等）
            print(f"Error in background task: {e}")
        finally:
            await mongo.close()

    @staticmethod
    async def do_abstract(
        messages: str,
        llm_client: LLMClient,
        llm_name: str,
        llm_url: str,
        llm_key: str,
    ):
        prompt_list = [
            {
                "role": "system",
                "content": f"### 这是历史对话：\n{messages} \n ### 请对聊天内容总结为一个标题，标题长度不超过10个字，请勿返回其他任何内容。",
            }
        ]
        abstract_title = await llm_client.get_response_chat(
            prompt_list,
            "deepseek-chat" if llm_name == "deepseek" else llm_name,
            llm_url,
            llm_key,
        )
        return abstract_title

    @staticmethod
    async def do_multi_agent(
        agent: Agent,
        messages: str,
        question: str,
        current_user_id: int,
        session_id: str,
        mongo: MongoDBManager,
        llm_client: LLMClient,
        llm_name: str,
        llm_url: str,
        llm_key: str,
    ) -> AsyncGenerator[str, None]:
        """
        处理代理响应并生成事件流的异步函数

        参数:
            agent: 代理对象，需要有completion方法
            messages: 历史消息
            question: 用户输入的问句
            session_id: 当前会话ID
            mongo: MongoDB操作对象

        返回:
            异步生成器，生成JSON格式的事件字符串
        """
        question_message = f"""
            这是历史对话消息：
            {messages}
            这是用户的当前消息：
            {question}
            如果历史信息没有用处，以及用户没有明确意图时，您只需要正常回答即可
        """
        message_chunk = ""
        message_text = ""

        async for result in agent.completion(question_message):
            if result["type"] == "thought":
                message_chunk += result["content"]
                yield json.dumps(
                    {"event": "thought", "data": result["content"]}
                ) + "\n\n"

            if result["type"] == "text":
                message_text += result["content"]
                yield json.dumps({"event": "text", "data": result["content"]}) + "\n\n"

            if result["type"] == "end":
                message_thought = {
                    "role": "system",
                    "content": message_chunk,
                    "type": "thought",
                    "timestamp": datetime.now().isoformat(),
                }
                await mongo.add_message(session_id, message_thought)

                message_result = {
                    "role": "system",
                    "content": message_text,
                    "type": "text",
                    "timestamp": datetime.now().isoformat(),
                }
                await mongo.add_message(session_id, message_result)

                message_chunk = ""
                message_text = ""
                yield json.dumps({"event": "end", "data": ""}) + "\n\n"

        asyncio.create_task(
            App_A2A.update_session_title(
                current_user_id,
                session_id,
                llm_client,
                llm_name,
                llm_url,
                llm_key,
                mongo,
            )
        )

    @staticmethod
    async def do_llm_thought(
        mongo: MongoDBManager,
        current_user_id: int,
        session_id: str,
        llm_client: LLMClient,
        core_llm_name: str,
        core_llm_url: str,
        core_llm_key: str,
    ) -> AsyncGenerator[str, None]:
        """
        处理LLM流式响应并生成事件流的异步函数

        参数:
            mongo: MongoDB操作对象
            current_user: 当前用户对象
            session_id: 会话ID
            llm_client: LLM客户端对象
            core_llm_url: LLM服务URL
            core_llm_key: LLM API密钥

        返回:
            异步生成器，生成JSON格式的事件字符串
        """
        # 获取会话消息
        messages_find = await mongo.get_session_by_ids(str(current_user_id), session_id)
        question_message = messages_find["messages"]

        message_thought = ""
        message_text = ""

        # 处理LLM流式响应
        async for result in llm_client.get_stream_response_reasion_and_content(
            question_message,
            llm_url=core_llm_url,
            api_key=core_llm_key,
            model_name="deepseek-reasoner"
            if core_llm_name == "deepseek"
            else core_llm_name,
        ):
            if result["type"] == "thought":
                message_thought += result["content"]
            if result["type"] == "text":
                message_text += result["content"]

            # 生成事件流
            yield json.dumps(
                {"event": result["type"], "data": result["content"]}
            ) + "\n\n"

        # 保存思考过程到数据库
        thought_message = {
            "role": "system",
            "content": message_thought,
            "type": "thought",
            "timestamp": datetime.now().isoformat(),
        }
        await mongo.add_message(session_id, thought_message)

        # 保存最终文本到数据库
        text_message = {
            "role": "system",
            "content": message_text,
            "type": "text",
            "timestamp": datetime.now().isoformat(),
        }
        await mongo.add_message(session_id, text_message)

        asyncio.create_task(
            App_A2A.update_session_title(
                current_user_id,
                session_id,
                llm_client,
                core_llm_name,
                core_llm_url,
                core_llm_key,
                mongo,
            )
        )

    @staticmethod
    async def do_llm(
        mongo: MongoDBManager,
        current_user_id: str,
        session_id: str,
        llm_client: LLMClient,
        core_llm_name: str,
        core_llm_url: str,
        core_llm_key: str,
    ) -> AsyncGenerator[str, None]:
        """
        流式获取LLM响应并保存结果的异步函数

        参数:
            mongo: MongoDB数据库操作对象
            current_user: 当前用户对象
            session_id: 会话ID
            llm_client: LLM客户端对象
            core_llm_url: LLM服务端点URL
            core_llm_key: LLM API密钥

        返回:
            异步生成器，产生JSON格式的文本事件流
        """
        # 获取历史消息
        messages = await mongo.get_session_by_ids(str(current_user_id), session_id)
        message_text = ""

        params = {"extra_body": {"thinking": {"type": "disabled"}}}

        # 流式获取LLM响应
        async for chunk in llm_client.get_stream_response_reasion_and_content(
            messages["messages"],
            llm_url=core_llm_url,
            api_key=core_llm_key,
            model_name="deepseek-chat"
            if core_llm_name == "deepseek"
            else core_llm_name,
            **params if core_llm_name == "doubao-seed-1-6" else {},
        ):
            message_text += chunk["content"]
            yield json.dumps({"event": "text", "data": chunk["content"]}) + "\n\n"

        # 保存完整响应到数据库
        await mongo.add_message(
            session_id,
            {
                "role": "system",
                "content": message_text,
                "type": "text",
                "timestamp": datetime.now().isoformat(),
            },
        )

        asyncio.create_task(
            App_A2A.update_session_title(
                current_user_id,
                session_id,
                llm_client,
                core_llm_name,
                core_llm_url,
                core_llm_key,
                mongo,
            )
        )

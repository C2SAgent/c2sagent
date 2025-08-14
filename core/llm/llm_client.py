import asyncio
import json
import logging
import os
import re
import shutil
import time
from typing import AsyncGenerator

from fastmcp import Client
from mcp.types import TextContent, Tool
from openai import AsyncOpenAI
import datetime


class LLMClient:
    def __init__(self, llm_url="", api_key="") -> None:
        self.api_key: str = api_key
        self.llm_url: str = llm_url
        # self.client: AsyncOpenAI = AsyncOpenAI(
        #     api_key=self.api_key, base_url=self.llm_url
        # )
        pass

    async def get_stream_response(
        self, messages: list[dict[str, str]], llm_url, api_key
    ) -> AsyncGenerator[str, None]:
        self.llm_url = llm_url
        self.api_key = api_key
        client: AsyncOpenAI = AsyncOpenAI(api_key=self.api_key, base_url=self.llm_url)
        print("大模型开始了流式")
        print(messages)
        response = await client.chat.completions.create(
            messages=messages, stream=True, model="deepseek-reasoner"
        )
        async for chunk in response:
            delta = chunk.choices[0].delta
            if delta.content:
                print("模型输出了：")
                print(delta.content)
                yield delta.content

    async def get_response(
        self, messages: list[dict[str, str]], llm_url=None, api_key=None
    ) -> str:
        time.sleep(1)
        # if llm_url:
        print("==============================get_response=============================")
        print(llm_url + "======")
        print(api_key + "======")
        print(messages)
        llm_url = llm_url
        api_key = api_key

        client: AsyncOpenAI = AsyncOpenAI(api_key=api_key, base_url=llm_url)
        response = await client.chat.completions.create(
            messages=messages,
            stream=False,
            model="deepseek-reasoner",
            temperature=1.3,
            max_tokens=8192,
        )
        logging.info(f"Thinking: {response.choices[0].message.reasoning_content}")
        logging.info(
            f"AnswerContent=====================: {response.choices[0].message.content}"
        )
        return response.choices[0].message.content

    async def get_stream_com_response(
        self, messages: list[dict[str, str]], llm_url=None, api_key=None
    ) -> str:
        self.llm_url = llm_url
        self.api_key = api_key
        client: AsyncOpenAI = AsyncOpenAI(api_key=self.api_key, base_url=self.llm_url)
        print("大模型开始了流式")
        print(messages)
        response = await client.chat.completions.create(
            messages=messages, stream=True, model="deepseek-reasoner"
        )

        result = ""
        async for chunk in response:
            delta = chunk.choices[0].delta
            if delta.reasoning_content:
                result += delta.reasoning_content
            if delta.content:
                yield delta.content

        yield result

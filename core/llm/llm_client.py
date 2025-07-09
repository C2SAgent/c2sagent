import json
import logging
import os
import re
import shutil
from typing import AsyncGenerator

from fastmcp import Client
from mcp.types import TextContent, Tool
from openai import AsyncOpenAI
import datetime

class LLMClient:
    def __init__(self, llm_url: str, api_key: str) -> None:
        self.api_key: str = api_key
        self.llm_url: str = llm_url
        print("=====================================================llm")
        print(self.llm_url)
        print(self.api_key)
        self.client: AsyncOpenAI = AsyncOpenAI(
            api_key=self.api_key, base_url=self.llm_url
        )

    async def get_stream_response(
        self, messages: list[dict[str, str]], llm_url, api_key
    ) -> AsyncGenerator[str, None]:
        self.llm_url = llm_url
        self.api_key = api_key
        print("=====================================================llm")
        print(self.llm_url)
        print(self.api_key)
        self.client: AsyncOpenAI = AsyncOpenAI(
            api_key=self.api_key, base_url=self.llm_url
        )
        response = await self.client.chat.completions.create(
            messages=messages,
            stream=True,
            model="deepseek-chat",
            temperature=1.3,
            max_tokens=8192,
        )
        async for chunk in response:
            delta = chunk.choices[0].delta
            if delta.content:
                yield delta.content

    async def get_response(self, messages: list[dict[str, str]], llm_url, api_key) -> str:
        self.llm_url = llm_url
        self.api_key = api_key
        self.client: AsyncOpenAI = AsyncOpenAI(
            api_key=self.api_key, base_url=self.llm_url
        )
        response = await self.client.chat.completions.create(
            messages=messages,
            stream=False,
            model="deepseek-reasoner",
            temperature=1.3,
            max_tokens=8192,
        )
        logging.info(f"Thinking: {response.choices[0].message.reasoning_content}")
        return response.choices[0].message.content


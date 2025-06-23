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
    def __init__(self, api_key: str) -> None:
        self.api_key: str = api_key
        self.client: AsyncOpenAI = AsyncOpenAI(
            api_key=self.api_key, base_url="https://api.deepseek.com"
        )

    async def get_stream_response(
        self, messages: list[dict[str, str]]
    ) -> AsyncGenerator[str, None]:
        response = await self.client.chat.completions.create(
            messages=messages,
            stream=True,
            model="deepseek-response",
            temperature=1.3,
            max_tokens=8192,
        )
        async for chunk in response:
            delta = chunk.choices[0].delta
            if delta.content:
                yield delta.content

    async def get_response(self, messages: list[dict[str, str]]) -> str:
        print("=============================================================")
        print(messages)
        print("=============================================================")
        response = await self.client.chat.completions.create(
            messages=messages,
            stream=False,
            model="deepseek-reasoner",
            temperature=1.3,
            max_tokens=8192,
        )
        logging.info(f"Thinking: {response.choices[0].message.reasoning_content}")
        return response.choices[0].message.content


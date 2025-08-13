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


async def main():
    llm_client = LLMClient("None", "None")
    # result = await llm_client.get_response(
    #     [
    #         {
    #             "role": "system",
    #             "content": 'You are a helpful assistant  have access to these services and the tools they offer:\n\nService name: video_upload\n\n            Tool Name: bilibili_video_upload\n            Description: 这是用来进行bilibili视频上传使用的，你在使用该函数时，至少拥有四个参数，video_title，video_url，cover_url，user_id，如果你没有video_title参数，你可以使用测试投稿；但是video_url，cover_url必须为真实的，如果你没有，请使用其他工具先获取两个真实的参数，然后再使用该函数。\n            Arguments:\n            - video_title: No description (required)\n- video_desc: No description\n- dynamic_text: No description\n- video_url: No description (required)\n- cover_url: No description (required)\n- user_id: No description (required)\n- sessdata: No description\n- jct: No description\n        \n\n            Tool Name: bilibili_video_get_url\n            Description: 这是用来获取bilibili的video_url和cover_url的，他会生成一个真实的视频和封面链接，他不需要传递任何参数，可以直接获取\n            Arguments:\n            \n        \nChoose the appropriate tool based on the user\'s question. If no tool is needed, reply directly.\n\nIMPORTANT: When you need to use a tool, you must ONLY respond with the exact JSON list object format below, nothing else:\n[{\n    "tool": "tool-name-1",\n    "arguments": {\n        "argument-name": "value"\n    }\n},\n{\n    "tool": "tool-name-2",\n    "arguments": {\n        "argument-name": "value"\n    }\n},]\n\nWhen using the tool, user will return the result, so please be careful to distinguish it.\nWhen the user does not provide a specific date, the system uses 2025-08-07 as the baseline to coumpute the target date based on the user\'s intentThe dates/times you provide should must match the user\'s input exactly, be factually accurate, and must not fabricate false dates.After receiving a tool\'s response:\n1. Transform the raw data into a natural, conversational response\n2. Keep responses concise but informative\n3. Focus on the most relevant information\n4. Use appropriate context from the user\'s question\n5. Avoid simply repeating the raw data\n\nPlease use only the tools that are explicitly defined above.',
    #         },
    #         {"role": "user", "content": "用户要求使用mcp工具生成并上传视频到Bilibili，请协助完成该任务"},
    #     ],
    #     llm_url="https://api.deepseek.com/v1",
    #     api_key="sk-7f49c72dbe9a4284b156701b84aa42a8",
    # )
    # print(result)
    # result = await llm_client.get_response(
    #     [
    #         {
    #             "role": "system",
    #             "content": 'You are a helpful assistant  have access to these services and the tools they offer:\n\nService name: video_upload\n\n            Tool Name: bilibili_video_upload\n            Description: 这是用来进行bilibili视频上传使用的，你在使用该函数时，至少拥有四个参数，video_title，video_url，cover_url，user_id，如果你没有video_title参数，你可以使用测试投稿；但是video_url，cover_url必须为真实的，如果你没有，请使用其他工具先获取两个真实的参数，然后再使用该函数。\n            Arguments:\n            - video_title: No description (required)\n- video_desc: No description\n- dynamic_text: No description\n- video_url: No description (required)\n- cover_url: No description (required)\n- user_id: No description (required)\n- sessdata: No description\n- jct: No description\n        \n\n            Tool Name: bilibili_video_get_url\n            Description: 这是用来获取bilibili的video_url和cover_url的，他会生成一个真实的视频和封面链接，他不需要传递任何参数，可以直接获取\n            Arguments:\n            \n        \nChoose the appropriate tool based on the user\'s question. If no tool is needed, reply directly.\n\nIMPORTANT: When you need to use a tool, you must ONLY respond with the exact JSON list object format below, nothing else:\n[{\n    "tool": "tool-name-1",\n    "arguments": {\n        "argument-name": "value"\n    }\n},\n{\n    "tool": "tool-name-2",\n    "arguments": {\n        "argument-name": "value"\n    }\n},]\n\nWhen using the tool, user will return the result, so please be careful to distinguish it.\nWhen the user does not provide a specific date, the system uses 2025-08-07 as the baseline to coumpute the target date based on the user\'s intentThe dates/times you provide should must match the user\'s input exactly, be factually accurate, and must not fabricate false dates.After receiving a tool\'s response:\n1. Transform the raw data into a natural, conversational response\n2. Keep responses concise but informative\n3. Focus on the most relevant information\n4. Use appropriate context from the user\'s question\n5. Avoid simply repeating the raw data\n\nPlease use only the tools that are explicitly defined above.',
    #         },
    #         {"role": "user", "content": "用户要求使用mcp工具生成并上传视频到Bilibili，请协助完成该任务"},
    #     ],
    #     llm_url="https://api.deepseek.com/v1",
    #     api_key="sk-0ba18b6b63c84127b0873f1253b527a1",
    # )
    # print(result)
    async for chunk in llm_client.get_stream_response(
        [
            {
                "role": "system",
                "content": 'You are a helpful assistant  have access to these services and the tools they offer:\n\nService name: video_upload\n\n            Tool Name: bilibili_video_upload\n            Description: 这是用来进行bilibili视频上传使用的，你在使用该函数时，至少拥有四个参数，video_title，video_url，cover_url，user_id，如果你没有video_title参数，你可以使用测试投稿；但是video_url，cover_url必须为真实的，如果你没有，请使用其他工具先获取两个真实的参数，然后再使用该函数。\n            Arguments:\n            - video_title: No description (required)\n- video_desc: No description\n- dynamic_text: No description\n- video_url: No description (required)\n- cover_url: No description (required)\n- user_id: No description (required)\n- sessdata: No description\n- jct: No description\n        \n\n            Tool Name: bilibili_video_get_url\n            Description: 这是用来获取bilibili的video_url和cover_url的，他会生成一个真实的视频和封面链接，他不需要传递任何参数，可以直接获取\n            Arguments:\n            \n        \nChoose the appropriate tool based on the user\'s question. If no tool is needed, reply directly.\n\nIMPORTANT: When you need to use a tool, you must ONLY respond with the exact JSON list object format below, nothing else:\n[{\n    "tool": "tool-name-1",\n    "arguments": {\n        "argument-name": "value"\n    }\n},\n{\n    "tool": "tool-name-2",\n    "arguments": {\n        "argument-name": "value"\n    }\n},]\n\nWhen using the tool, user will return the result, so please be careful to distinguish it.\nWhen the user does not provide a specific date, the system uses 2025-08-07 as the baseline to coumpute the target date based on the user\'s intentThe dates/times you provide should must match the user\'s input exactly, be factually accurate, and must not fabricate false dates.After receiving a tool\'s response:\n1. Transform the raw data into a natural, conversational response\n2. Keep responses concise but informative\n3. Focus on the most relevant information\n4. Use appropriate context from the user\'s question\n5. Avoid simply repeating the raw data\n\nPlease use only the tools that are explicitly defined above.',
            },
            {"role": "user", "content": "您好"},
        ],
        llm_url="https://api.deepseek.com/v1",
        api_key="sk-7f49c72dbe9a4284b156701b84aa42a8",
    ):
        print(chunk)


if __name__ == "__main__":
    asyncio.run(main())

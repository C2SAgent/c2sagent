import logging
from typing import AsyncGenerator
from openai import AsyncOpenAI


class LLMClient:
    def __init__(self, llm_url="", api_key="") -> None:
        self.api_key: str = api_key
        self.llm_url: str = llm_url

    async def get_stream_response_chat(
        self, messages: list[dict[str, str]], llm_url=None, api_key=None
    ) -> AsyncGenerator[str, None]:
        if llm_url and api_key:
            self.llm_url = llm_url
            self.api_key = api_key
        client: AsyncOpenAI = AsyncOpenAI(api_key=self.api_key, base_url=self.llm_url)

        response = await client.chat.completions.create(
            messages=messages, stream=True, model="deepseek-chat"
        )
        async for chunk in response:
            delta = chunk.choices[0].delta
            if delta.content:
                yield {"type": "text", "content": delta.content}

    async def get_stream_response_reasion_and_content(
        self, messages: list[dict[str, str]], llm_url=None, api_key=None
    ) -> AsyncGenerator[str, None]:
        if llm_url and api_key:
            self.llm_url = llm_url
            self.api_key = api_key
        client: AsyncOpenAI = AsyncOpenAI(api_key=self.api_key, base_url=self.llm_url)

        response = await client.chat.completions.create(
            messages=messages, stream=True, model="deepseek-reasoner"
        )
        async for chunk in response:
            delta = chunk.choices[0].delta
            if delta.reasoning_content:
                yield {"type": "thought", "content": delta.reasoning_content}
            if delta.content:
                yield {"type": "text", "content": delta.content}

    async def get_response(
        self, messages: list[dict[str, str]], llm_url=None, api_key=None
    ) -> str:
        if llm_url and api_key:
            self.llm_url = llm_url
            self.api_key = api_key

        client: AsyncOpenAI = AsyncOpenAI(api_key=self.api_key, base_url=self.llm_url)
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
    ) -> AsyncGenerator[str, None]:
        if llm_url and api_key:
            self.llm_url = llm_url
            self.api_key = api_key
        client: AsyncOpenAI = AsyncOpenAI(api_key=self.api_key, base_url=self.llm_url)
        response = await client.chat.completions.create(
            messages=messages, stream=True, model="deepseek-reasoner"
        )

        result = ""
        async for chunk in response:
            delta = chunk.choices[0].delta
            if delta.reasoning_content:
                yield delta.reasoning_content
            if delta.content:
                result += delta.content

        yield result

    async def get_response_chat(
        self, messages: list[dict[str, str]], llm_url=None, api_key=None
    ):
        if llm_url and api_key:
            self.llm_url = llm_url
            self.api_key = api_key
        client: AsyncOpenAI = AsyncOpenAI(api_key=self.api_key, base_url=self.llm_url)

        response = await client.chat.completions.create(
            messages=messages, stream=False, model="deepseek-chat"
        )
        return response.choices[0].message.content

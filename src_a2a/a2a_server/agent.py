import asyncio
import json
import re
from collections.abc import AsyncGenerator, Callable, Generator
from pathlib import Path
from typing import Literal

from jinja2 import Template

from src_a2a.a2a_server.mcp_manager import call_mcp_client, call_mcp_client_streaming

dir_path = Path(__file__).parent

with Path(dir_path / "decide.jinja").open("r") as f:
    decide_template = Template(f.read())

with Path(dir_path / "tool.jinja").open("r") as f:
    tool_template = Template(f.read())

with Path(dir_path / "called_tools_history.jinja").open("r") as f:
    called_tools_history_template = Template(f.read())


class Agent:
    """Agent for interacting with the Google Gemini LLM in different modes."""

    def __init__(
        self,
        mode: Literal["complete", "stream"] = "stream",
        token_stream_callback: Callable[[str], None] | None = None,
        mcp_url: str | None = None,
        agent_index: int | None = None,
        mcp_server_id: int | None = None,
    ):
        self.mode = mode
        self.token_stream_callback = token_stream_callback
        self.mcp_url = mcp_url
        self.agent_index = agent_index
        self.mcp_server_id = mcp_server_id

    async def decide(
        self, question: str, called_tools: list[dict] | None = None
    ) -> Generator[str, None]:
        """Decide which tool to use to answer the question.

        Args:
            question (str): The question to answer.
            called_tools (list[dict]): The tools that have been called.
        """

        print(
            "=====================call_mcp_client_bilibili==========================="
        )
        result = await call_mcp_client(
            self.mcp_url,
            query=question,
            agent_index=self.agent_index,
            mcp_server_id=self.mcp_server_id,
        )
        return result

    async def completion(self, question: str) -> AsyncGenerator[str]:
        """Stream the process of answering a question, possibly involving tool calls.

        Args:
            question (str): The question to answer.

        Yields:
            dict: Streaming output, including intermediate steps and final result.
        """  # noqa: E501

        response = await self.decide(question)

        return response

    async def decide_streaming(
        self, question: str, called_tools: list[dict] | None = None
    ) -> AsyncGenerator[str, None]:
        """Decide which tool to use to answer the question.

        Args:
            question (str): The question to answer.
            called_tools (list[dict]): The tools that have been called.
        """
        async for chunk in call_mcp_client_streaming(
            self.mcp_url,
            query=question,
            agent_index=self.agent_index,
            mcp_server_id=self.mcp_server_id,
        ):
            yield chunk

    async def stream(self, question: str) -> AsyncGenerator[str]:
        """Stream the process of answering a question, possibly involving tool calls.

        Args:
            question (str): The question to answer.

        Yields:
            dict: Streaming output, including intermediate steps and final result.

        """  # noqa: E501

        async for chunk in await self.decide_streaming(question):
            yield chunk

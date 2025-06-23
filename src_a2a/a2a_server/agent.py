import asyncio
import json
import re
from collections.abc import AsyncGenerator, Callable, Generator
from pathlib import Path
from typing import Literal

from jinja2 import Template

from constant import GOOGLE_API_KEY
from mcp_manager import call_mcp_client

dir_path = Path(__file__).parent

with Path(dir_path / 'decide.jinja').open('r') as f:
    decide_template = Template(f.read())

with Path(dir_path / 'tool.jinja').open('r') as f:
    tool_template = Template(f.read())

with Path(dir_path / 'called_tools_history.jinja').open('r') as f:
    called_tools_history_template = Template(f.read())


class Agent:
    """Agent for interacting with the Google Gemini LLM in different modes."""

    def __init__(
        self,
        mode: Literal['complete', 'stream'] = 'stream',
        token_stream_callback: Callable[[str], None] | None = None,
        mcp_url: str | None = None,
    ):
        self.mode = mode
        self.token_stream_callback = token_stream_callback
        self.mcp_url = mcp_url

    async def decide(
        self, question: str, called_tools: list[dict] | None = None
    ) -> Generator[str, None]:
        """Decide which tool to use to answer the question.

        Args:
            question (str): The question to answer.
            called_tools (list[dict]): The tools that have been called.
        """
        result = await call_mcp_client(self.mcp_url, query=question)
        return result

    async def stream(self, question: str) -> AsyncGenerator[str]:
        """Stream the process of answering a question, possibly involving tool calls.

        Args:
            question (str): The question to answer.

        Yields:
            dict: Streaming output, including intermediate steps and final result.
        """  # noqa: E501

        response = await self.decide(question)

        return response


# if __name__ == '__main__':
#     agent = Agent(
#         token_stream_callback=lambda token: print(token, end='', flush=True),
#         mcp_url='http://localhost:8000/chat/chat_with_mcp',
#     )

#     async def main():
#         """Main function."""
#         async for chunk in agent.stream('What is A2A Protocol?'):
#             print(chunk)

#     asyncio.run(main())

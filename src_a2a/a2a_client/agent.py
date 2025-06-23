import asyncio
import json
import re
from collections.abc import Callable, Generator
from pathlib import Path
from typing import Literal
from uuid import uuid4
import os

from project.core.llm_client import LLMClient

# import google.generativeai as genai
import uuid
import httpx
from a2a.client import A2ACardResolver, A2AClient
from a2a.types import (
    AgentCard,
    Message,
    MessageSendParams,
    Part,
    Role,
    SendStreamingMessageRequest,
    SendMessageResponse,
    SendMessageRequest,
    SendMessageSuccessResponse,
    SendStreamingMessageSuccessResponse,
    TaskStatusUpdateEvent,
    TextPart,
)
from jinja2 import Template

# from no_llm_framework.client.constant import GOOGLE_API_KEY


dir_path = Path(__file__).parent

with Path(dir_path / 'decide.jinja').open('r') as f:
    decide_template = Template(f.read())

with Path(dir_path / 'agents.jinja').open('r') as f:
    agents_template = Template(f.read())

with Path(dir_path / 'agent_answer.jinja').open('r') as f:
    agent_answer_template = Template(f.read())


async def stream_llm(prompt: str) -> Generator[str]:
    """Stream LLM response.

    Args:
        prompt (str): The prompt to send to the LLM.

    Returns:
        Generator[str, None, None]: A generator of the LLM response.
    """
    llm_client = LLMClient(os.getenv("API_KEY"))
    messages = [{"role": "system", "content": prompt}]
    response = await llm_client.get_response(messages)
    return response


class Agent:
    """Agent for interacting with the Google Gemini LLM in different modes."""

    def __init__(
        self,
        mode: Literal['complete', 'stream'] = 'stream',
        token_stream_callback: Callable[[str], None] | None = None,
        agent_urls: list[str] | None = None,
        agent_prompt: str | None = None,
    ):
        self.mode = mode
        self.token_stream_callback = token_stream_callback
        self.agent_urls = agent_urls
        self.agents_registry: dict[str, AgentCard] = {}

    async def get_agents(self) -> tuple[dict[str, AgentCard], str]:
        """Retrieve agent cards from all agent URLs and render the agent prompt.

        Returns:
            tuple[dict[str, AgentCard], str]: A dictionary mapping agent names to AgentCard objects, and the rendered agent prompt string.
        """  # noqa: E501
        async with httpx.AsyncClient() as httpx_client:
            card_resolvers = [
                A2ACardResolver(httpx_client, url) for url in self.agent_urls
            ]
            agent_cards = await asyncio.gather(
                *[
                    card_resolver.get_agent_card()
                    for card_resolver in card_resolvers
                ]
            )
            agents_registry = {
                agent_card.name: agent_card for agent_card in agent_cards
            }
            agent_prompt = agents_template.render(agent_cards=agent_cards)
            return agents_registry, agent_prompt

    async def call_llm(self, prompt: str) -> str:
        """Call the LLM with the given prompt and return the response as a string or generator.

        Args:
            prompt (str): The prompt to send to the LLM.

        Returns:
            str or Generator[str]: The LLM response as a string or generator, depending on mode.
        """  # noqa: E501
        return await stream_llm(prompt)

    async def decide(
        self,
        question: str,
        agents_prompt: str,
        called_agents: list[dict] | None = None,
    ) -> Generator[str, None]:
        """Decide which agent(s) to use to answer the question.

        Args:
            question (str): The question to answer.
            agents_prompt (str): The prompt describing available agents.
            called_agents (list[dict] | None): Previously called agents and their answers.

        Returns:
            Generator[str, None]: The LLM's response as a generator of strings.
        """  # noqa: E501
        if called_agents:
            call_agent_prompt = agent_answer_template.render(
                called_agents=called_agents
            )
        else:
            call_agent_prompt = ''
        prompt = decide_template.render(
            question=question,
            agent_prompt=agents_prompt,
            call_agent_prompt=call_agent_prompt,
        )
        return await self.call_llm(prompt)

    def extract_agents(self, response: str) -> list[dict]:
        """Extract the agents from the response.

        Args:
            response (str): The response from the LLM.
        """
        pattern = r'```json\n(.*?)\n```'
        match = re.search(pattern, response, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        return []

    async def send_message_to_an_agent(
        self, agent_card: AgentCard, message: str
    ):
        """Send a message to a specific agent and yield the streaming response.

        Args:
            agent_card (AgentCard): The agent to send the message to.
            message (str): The message to send.

        Yields:
            str: The streaming response from the agent.
        """

        # client = self.remote_agent_connections[agent_name]
        
        async with httpx.AsyncClient(timeout=500) as httpx_client:
            client = A2AClient(httpx_client, agent_card=agent_card, url=agent_card.url)
            message_id = str(uuid.uuid4())
            task_id = str(uuid.uuid4())
            context_id = str(uuid.uuid4())
            payload = {
                "message": {
                    "role": "user",
                    "parts": [{"type": "text", "text": message}],
                    "messageId": message_id,
                },
            }

            if task_id:
                payload["message"]["taskId"] = task_id

            if context_id:
                payload["message"]["contextId"] = context_id
            
            message_request = SendMessageRequest(
                id=message_id, params=MessageSendParams.model_validate(payload)
            )
            send_response: SendMessageResponse = await client.send_message(message_request)
            
            return send_response.root.result.status.message.parts[0].root.text

            # return send_response


    async def stream(self, question: str):
        """Stream the process of answering a question, possibly involving multiple agents.

        Args:
            question (str): The question to answer.

        Yields:
            str: Streaming output, including agent responses and intermediate steps.
        """  # noqa: E501
        agent_answers: list[dict] = []

        agents_registry, agent_prompt = await self.get_agents()
        response = await self.decide(
            question, agent_prompt, agent_answers
        )

        agents = self.extract_agents(response)
        if agents:
            for agent in agents:
                agent_card = agents_registry[agent['name']]
                agent_response = await self.send_message_to_an_agent(
                    agent_card, agent['prompt']
                )
                print(agent_response)
                # match = re.search(
                #     r'<Answer>(.*?)</Answer>', agent_response, re.DOTALL
                # )
                # answer = match.group(1).strip() if match else agent_response
                agent_answers.append(
                    {
                        'name': agent['name'],
                        'prompt': agent['prompt'],
                        'answer': agent_response,
                    }
                )
            return agent_answers
        else:
            return


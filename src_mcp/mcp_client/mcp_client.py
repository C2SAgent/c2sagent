import asyncio
import json
import logging
import os
import re
import shutil
from typing import AsyncGenerator

from dotenv import load_dotenv
from fastmcp import Client
from mcp.types import TextContent, Tool
from openai import AsyncOpenAI
import datetime

from core.llm.llm_client import LLMClient
from core.db.base import DatabaseManager
from model.model_agent import AgentCard, McpServer
from sqlalchemy.future import select

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
db = DatabaseManager(DATABASE_URL)


def load_mcp_config(file_path: str) -> dict[str, any]:
    with open(file_path, "r") as f:
        return json.load(f)


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class ChatSession:
    def __init__(self, servers: dict[str, Client], llm_client: LLMClient):
        self.servers: dict[str, Client] = servers
        self.llm_client: LLMClient = llm_client
        self.server_name: str = None

    async def process_llm_response(self, llm_response: str, mcp_server_id) -> str:
        try:
            json_match = re.search(r"\[.*?\]", llm_response, re.DOTALL)
            if json_match:
                json_content = json_match.group(0)
                logging.info(f"Extracted JSON content: {json_content}")
            else:
                json_content = llm_response

            tool_calls = json.loads(json_content)
            results = ""
            for tool_call in tool_calls:
                if "tool" in tool_call and "arguments" in tool_call:
                    logging.info(f"Executing tool: {tool_call['tool']}")
                    logging.info(f"With arguments: {tool_call['arguments']}")
                    mcp_config = {
                        "mcpServers": {
                            f"{self.server_name}": {
                                "command": "url",
                                "url": f"http://localhost:3000/mcp/{mcp_server_id}",
                            }
                        }
                    }
                    mcp_servers = {
                        server_name: parse_mcp_client(config)
                        for server_name, config in mcp_config["mcpServers"].items()
                    }

                    async with mcp_servers[f"{self.server_name}"] as server:
                        tools = await asyncio.wait_for(
                            server.list_tools(), timeout=60.0
                        )
                        if any(tool.name == tool_call["tool"] for tool in tools):
                            try:
                                result: list = await server.call_tool(
                                    tool_call["tool"],
                                    (
                                        tool_call["arguments"]
                                        if len(tool_call["arguments"]) > 0
                                        else None
                                    ),
                                )
                                logging.info(
                                    f"{tool_call['tool']} execution result: {result}"
                                )
                                results += f"{tool_call['tool']} execution result: {[res.text for res in filter(lambda x: True if isinstance(x, TextContent) else False, result)]}\n"
                            except Exception as e:
                                error_msg = f"Error executing tool: {str(e)}"
                                logging.error(error_msg)
                                return error_msg

            if results:
                logging.info(f"Final results: {results}")
                return results
            return "No server found with tools"
        except json.JSONDecodeError:
            logging.info("No valid JSON found in LLM response")
            return llm_response

    @staticmethod
    def format_for_llm(tool: Tool) -> str:
        args_desc = []
        if "properties" in tool.inputSchema:
            for param_name, param_info in tool.inputSchema["properties"].items():
                arg_desc = (
                    f"- {param_name}: {param_info.get('description', 'No description')}"
                )
                if param_name in tool.inputSchema.get("required", []):
                    arg_desc += " (required)"
                args_desc.append(arg_desc)

        return f"""
            Tool Name: {tool.name}
            Description: {tool.description}
            Arguments:
            {chr(10).join(args_desc)}
        """

    async def _get_agent_response(self, messages, mcp_server_id, agent_id):
        # 异步查询AgentCard
        agent_find = await db.fetch_one(AgentCard, id=agent_id)
        logging.info(f"Agent config: {agent_find.llm_url}, {agent_find.llm_key}")
        self.llm_client.llm_url = agent_find.llm_url
        self.llm_client.api_key = agent_find.llm_key

        # 异步查询McpServer
        mcp_server_find = await db.fetch_one(McpServer, id=mcp_server_id)
        self.server_name = mcp_server_find.name

        mcp_config = {
            "mcpServers": {
                f"{self.server_name}": {
                    "command": "url",
                    "url": f"http://localhost:3000/mcp/{mcp_server_id}",
                }
            }
        }

        mcp_servers = {
            server_name: parse_mcp_client(config)
            for server_name, config in mcp_config["mcpServers"].items()
        }
        tools_description = ""

        async with mcp_servers[f"{self.server_name}"] as server:
            tools = await server.list_tools()
            tools_description += f"Service name: {self.server_name}\n"
            tools_description += "\n".join(
                [self.format_for_llm(tool) for tool in tools]
            )

        system_message = (
            "You are a helpful assistant  have access to these services and the tools they offer:\n\n"
            # 工具描述prompt
            f"{tools_description}\n"
            "Choose the appropriate tool based on the user's question. "
            "If no tool is needed, reply directly.\n\n"
            "IMPORTANT: When you need to use a tool, you must ONLY respond with "
            "the exact JSON list object format below, nothing else:\n"
            "[{\n"
            '    "tool": "tool-name-1",\n'
            '    "arguments": {\n'
            '        "argument-name": "value"\n'
            "    }\n"
            "},\n"
            "{\n"
            '    "tool": "tool-name-2",\n'
            '    "arguments": {\n'
            '        "argument-name": "value"\n'
            "    }\n"
            "},]\n\n"
            "When using the tool, user will return the result, so please be careful to distinguish it.\n"
            # 时间处理prompt
            f"When the user does not provide a specific date, the system uses {datetime.date.today()} as the baseline to coumpute the target date based on the user's intent"
            "The dates/times you provide should must match the user's input exactly, be factually accurate, and must not fabricate false dates."
            "After receiving a tool's response:\n"
            "1. Transform the raw data into a natural, conversational response\n"
            "2. Keep responses concise but informative\n"
            "3. Focus on the most relevant information\n"
            "4. Use appropriate context from the user's question\n"
            "5. Avoid simply repeating the raw data\n\n"
            "Please use only the tools that are explicitly defined above."
        )
        messages = [{"role": "system", "content": system_message}] + messages
        llm_response = await self.llm_client.get_response(
            messages, self.llm_client.llm_url, self.llm_client.api_key
        )
        logging.info(f"\nAssistant: {llm_response}")

        result = await self.process_llm_response(llm_response, mcp_server_id)
        while result != llm_response:
            messages.append({"role": "assistant", "content": llm_response})
            messages.append({"role": "user", "content": result})
            llm_response = await self.llm_client.get_response(
                messages, self.llm_client.llm_url, self.llm_client.api_key
            )
            logging.info(f"\nAssistant: {llm_response}")
            result = await self.process_llm_response(llm_response, mcp_server_id)
        return result

    async def _get_agent_response_streaming(
        self, messages, mcp_server_id, agent_id
    ) -> AsyncGenerator[str, None]:
        # 异步查询AgentCard
        agent_find = await db.fetch_one(AgentCard, id=agent_id)
        logging.info(f"Agent config: {agent_find.llm_url}, {agent_find.llm_key}")
        self.llm_client.llm_url = agent_find.llm_url
        self.llm_client.api_key = agent_find.llm_key

        # 异步查询McpServer
        mcp_server_find = await db.fetch_one(McpServer, id=mcp_server_id)
        self.server_name = mcp_server_find.name

        mcp_config = {
            "mcpServers": {
                f"{self.server_name}": {
                    "command": "url",
                    "url": f"http://localhost:3000/mcp/{mcp_server_id}",
                }
            }
        }

        mcp_servers = {
            server_name: parse_mcp_client(config)
            for server_name, config in mcp_config["mcpServers"].items()
        }
        tools_description = ""

        async with mcp_servers[f"{self.server_name}"] as server:
            tools = await server.list_tools()
            tools_description += f"Service name: {self.server_name}\n"
            tools_description += "\n".join(
                [self.format_for_llm(tool) for tool in tools]
            )

        system_message = (
            "You are a helpful assistant  have access to these services and the tools they offer:\n\n"
            # 工具描述prompt
            f"{tools_description}\n"
            "Choose the appropriate tool based on the user's question. "
            "If no tool is needed, reply directly.\n\n"
            "IMPORTANT: When you need to use a tool, you must ONLY respond with "
            "the exact JSON list object format below, nothing else:\n"
            "[{\n"
            '    "tool": "tool-name-1",\n'
            '    "arguments": {\n'
            '        "argument-name": "value"\n'
            "    }\n"
            "},\n"
            "{\n"
            '    "tool": "tool-name-2",\n'
            '    "arguments": {\n'
            '        "argument-name": "value"\n'
            "    }\n"
            "},]\n\n"
            "When using the tool, user will return the result, so please be careful to distinguish it.\n"
            # 时间处理prompt
            f"When the user does not provide a specific date, the system uses {datetime.date.today()} as the baseline to coumpute the target date based on the user's intent"
            "The dates/times you provide should must match the user's input exactly, be factually accurate, and must not fabricate false dates."
            "After receiving a tool's response:\n"
            "1. Transform the raw data into a natural, conversational response\n"
            "2. Keep responses concise but informative\n"
            "3. Focus on the most relevant information\n"
            "4. Use appropriate context from the user's question\n"
            "5. Avoid simply repeating the raw data\n\n"
            "Please use only the tools that are explicitly defined above."
        )
        messages = [{"role": "system", "content": system_message}] + messages

        llm_response = ""
        print("====================mcp流式响应=======================")
        async for chunk in self.llm_client.get_stream_response(
            messages, self.llm_client.llm_url, self.llm_client.api_key
        ):
            print(chunk)
            llm_response += chunk
            event = {
                "is_task_complete": False,
                "require_user_input": False,
                "content": chunk,
            }
            yield event
        print("====================mcp流式响应结束=======================")

        logging.info(f"\nAssistant: {llm_response}")

        result = await self.process_llm_response(llm_response, mcp_server_id)
        while result != llm_response:
            messages.append({"role": "assistant", "content": llm_response})
            messages.append({"role": "user", "content": result})
            llm_response = ""
            print("====================mcp流式响应=======================")
            async for chunk in self.llm_client.get_stream_response(
                messages, self.llm_client.llm_url, self.llm_client.api_key
            ):
                llm_response += chunk
                event = {
                    "is_task_complete": False,
                    "require_user_input": False,
                    "content": chunk,
                }
                yield event
            print("====================mcp流式结束=======================")

            logging.info(f"\nAssistant: {llm_response}")
            result = await self.process_llm_response(llm_response, mcp_server_id)

        print("====================mcp完成答案=======================")
        yield {"is_task_complete": True, "require_user_input": False, "content": result}


def parse_mcp_client(config: dict[str, any]):
    command = shutil.which("npx") if config["command"] == "npx" else config["command"]
    if command is None:
        raise ValueError("Command not found")
    return Client(config["url"])

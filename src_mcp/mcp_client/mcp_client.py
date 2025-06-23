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

from project.core.llm_client import LLMClient

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

    async def process_llm_response(self, llm_response: str) -> str:
        try:
            # TODO: 需要扩展JSON验证
            json_match = re.search(r"\[.*?\]", llm_response, re.DOTALL)
            # 工具调用
            if json_match:
                json_content = json_match.group(0)
                logging.info(f"Extracted JSON content: {json_content}")
            # 非工具调用，普通对话
            else:
                json_content = llm_response
            

            tool_calls = json.loads(json_content)
            results = ""
            for tool_call in tool_calls:
                if "tool" in tool_call and "arguments" in tool_call:
                    logging.info(f"Executing tool: {tool_call['tool']}")
                    logging.info(f"With arguments: {tool_call['arguments']}")
                    for server_name in self.servers:
                        async with self.servers[server_name] as server:
                            tools = await server.list_tools()
                            if any(tool.name == tool_call["tool"] for tool in tools):
                                try:
                                    result: list = await server.call_tool(
                                        tool_call["tool"],
                                        tool_call["arguments"]
                                        if len(tool_call["arguments"]) > 0
                                        else None,
                                    )
                                    logging.info(
                                        f"{tool_call['tool']} execution result: {result}"
                                    )
                                    
                                    # 过滤文本信息
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

    async def _get_agent_response(self, messages):
        tools_description = ""
        for server_name in self.servers:
            async with self.servers[server_name] as server:
                tools = await server.list_tools()
                tools_description += f"Service name: {server_name}\n"
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
        messages = [{"role": "system", "content": system_message}]+messages
        llm_response = await self.llm_client.get_response(messages)
        logging.info(f"\nAssistant: {llm_response}")

        result = await self.process_llm_response(llm_response)
        while result != llm_response:
            messages.append({"role": "assistant", "content": llm_response})
            messages.append({"role": "user", "content": result})
            llm_response = await self.llm_client.get_response(messages)
            logging.info(f"\nAssistant: {llm_response}")
            result = await self.process_llm_response(llm_response)
        return result

    # TODO: 待完成流式agent接口
    async def get_agent_response_stream(self, messages):
        logging.info("\nAssistant:")
        async for llm_response in self.llm_client.get_stream_response(messages):
            result = await self.process_llm_response(llm_response)
            while result != llm_response:
                messages.append({"role": "assistant", "content": llm_response})
                messages.append({"role": "user", "content": result})
                async for llm_response in self.llm_client.get_stream_response(messages):
                    logging.info(f"\nAssistant: {llm_response}")
                    result = await self.process_llm_response(llm_response)
            return result


def parse_mcp_client(config: dict[str, any]):
    command = shutil.which("npx") if config["command"] == "npx" else config["command"]
    if command is None:
        raise ValueError("no")
    return Client(config["url"])

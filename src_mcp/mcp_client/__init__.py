import os
import logging
from typing import Optional
from contextlib import asynccontextmanager
from core.llm.llm_client import LLMClient
from src_mcp.mcp_client.mcp_client import load_mcp_config, parse_mcp_client

# 全局状态单例
_llm_client: Optional[LLMClient] = None
_mcp_servers: Optional[dict] = None


def get_api_key() -> str:
    """从环境变量获取 API Key"""
    api_key = "init"
    # api_key = os.getenv("API_KEY")
    if not api_key:
        raise ValueError("API Key not found in environment variables")
    return api_key


async def initialize_resources():
    """初始化全局资源（线程安全）"""
    logging.info("Initializing resources...")
    global _llm_client, _mcp_servers
    if _llm_client is None or _mcp_servers is None:
        try:
            mcp_config = load_mcp_config("src_mcp/mcp_client/configs_server.json")
            _mcp_servers = {
                server_name: parse_mcp_client(config)
                for server_name, config in mcp_config["mcpServers"].items()
            }
            _llm_client = LLMClient(llm_url="init", api_key=get_api_key())
            logging.info("Resources initialized")
        except Exception as e:
            logging.critical(f"Initialization failed: {e}")
            raise


def get_llm_client() -> LLMClient:
    """获取已初始化的LLM客户端"""
    if _llm_client is None:
        raise RuntimeError("LLMClient not initialized")
    return _llm_client


def get_mcp_servers() -> dict:
    """获取已初始化的MCP服务器配置"""
    if _mcp_servers is None:
        raise RuntimeError("MCP Servers not initialized")
    return _mcp_servers


@asynccontextmanager
async def lifespan(app):
    """FastAPI生命周期管理器"""
    await initialize_resources()
    yield
    # 清理逻辑（可选）
    global _llm_client, _mcp_servers
    _llm_client = None
    _mcp_servers = None

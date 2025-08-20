import click
import uvicorn
from a2a.server.agent_execution import AgentExecutor
from a2a.server.apps.jsonrpc import A2AStarletteApplication
from a2a.server.request_handlers.default_request_handler import (
    DefaultRequestHandler,
)
from a2a.server.tasks.inmemory_task_store import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard
from starlette.applications import Starlette
from starlette.routing import Route, Router
from starlette.requests import Request
from typing import Any, List
from a2a.server.request_handlers.jsonrpc_handler import JSONRPCHandler

from core.db.base_sync import DatabaseManager

from model.model_agent import AgentCard as AgentCard_

from src_a2a.a2a_server.agent_executor import CoreAgentExecutor
from starlette.responses import JSONResponse

from api.apps.agent.config import settings

DATABASE_SYNC_URL = settings.DATABASE_SYNC_URL
db = DatabaseManager(DATABASE_SYNC_URL)


class DynamicContextBuilder:
    """上下文构建器包装类，添加 agent_index 属性"""

    def __init__(self, original_builder, agent_index):
        """
        初始化上下文构建器

        :param original_builder: 原始上下文构建器对象
        :param agent_index: 要添加到上下文中的 agent 索引
        """
        self.original_builder = original_builder
        self.agent_index = agent_index

    def build(self, request: Request):
        """
        构建请求上下文

        :param request: Starlette 请求对象
        :return: 上下文对象
        """
        # 如果存在原始上下文构建器，使用它构建上下文
        if self.original_builder and hasattr(self.original_builder, "build"):
            context = self.original_builder.build(request)
        else:
            context = None

        # 添加 agent_index 到上下文
        if context:
            setattr(context, "agent_index", self.agent_index)
        return context


class DatabaseA2AStarletteApplication(A2AStarletteApplication):
    """最终解决方案：确保正确处理客户端请求路径"""

    def __init__(self, db: Any, http_handler: DefaultRequestHandler):
        self.db = db
        # 使用临时卡片初始化
        temp_card = AgentCard(
            name="Temporary Agent",
            description="Initial agent card",
            url="http://localhost:9999/a2a/default",
            version="1.0.0",
            defaultInputModes=["text"],
            defaultOutputModes=["text"],
            capabilities=AgentCapabilities(
                inputModes=["text"], outputModes=["text"], streaming=True
            ),
            skills=[],
            examples=[],
        )

        self.task_store = InMemoryTaskStore()

        self.agent_card = temp_card
        self.http_handler = http_handler
        self.handler = JSONRPCHandler(
            agent_card=self.agent_card, request_handler=self.http_handler
        )

        # super().__init__(agent_card=temp_card, http_handler=self.http_handler)

        # 创建子路由器处理特定agent路径
        self.agent_router = Router()

        # 在子路由器上注册路由
        self.agent_router.add_route(
            "/.well-known/agent.json", self._handle_dynamic_agent_card, methods=["GET"]
        )
        self.agent_router.add_route("/", self._handle_dynamic_request, methods=["POST"])

    def _get_agent_card_from_db(self, agent_index: str, request: Request) -> AgentCard:
        """从数据库构建AgentCard（使用您提供的查询逻辑）"""

        # # 获取agent基本信息
        agent_data = self.db.fetch_one(AgentCard_, id=agent_index)

        return AgentCard(
            name=agent_data.name,
            description=agent_data.description,
            url=f"http://{request.url.hostname}:{request.url.port}/a2a/{agent_index}",
            version=agent_data.version,
            defaultInputModes=["text"],
            defaultOutputModes=["text"],
            capabilities=AgentCapabilities(
                inputModes=["text"],
                outputModes=["text"],
                streaming=agent_data.streaming,
            ),
            skills=[],
            examples=agent_data.examples or [],
        )

    def routes(
        self,
        rpc_url: str = "/",
        extended_agent_card_url: str = "/agent/authenticatedExtendedCard",
        **kwargs,
    ) -> List[Route]:
        """路由配置 - 直接定义两个独立路由"""
        routes = [
            Route(rpc_url, self._handle_requests, methods=["POST"]),
            # 动态agent卡片路由
            Route(
                "/a2a/{agent_index}/.well-known/agent.json",
                self._handle_dynamic_agent_card,
                methods=["GET"],
            ),
            # 动态agent请求路由
            Route("/a2a/{agent_index}", self._handle_dynamic_request, methods=["POST"]),
        ]

        if self.agent_card and self.agent_card.supportsAuthenticatedExtendedCard:
            routes.append(
                Route(
                    extended_agent_card_url,
                    self._handle_get_authenticated_extended_agent_card,
                    methods=["GET"],
                )
            )

        return routes

    async def _handle_dynamic_agent_card(self, request: Request) -> JSONResponse:
        """处理动态agent卡片请求"""
        agent_index = request.path_params["agent_index"]
        try:
            card = self._get_agent_card_from_db(agent_index, request)
            return JSONResponse(card.dict())
        except Exception as e:
            return JSONResponse(
                {"error": f"Agent not found: {str(e)}"}, status_code=404
            )

    async def _handle_dynamic_request(self, request: Request) -> JSONResponse:
        """处理动态agent请求"""
        # 初始化变量
        original_card = None
        original_context_builder = None

        try:
            agent_index = request.path_params.get("agent_index")
            self.task_store = InMemoryTaskStore()
            self.http_handler.agent_executor = CoreAgentExecutor(
                agent_index=agent_index, isStreaming=True
            )

            if not agent_index:
                return JSONResponse(
                    {"error": "Missing agent_index in path parameters"}, status_code=400
                )

            # 保存原始状态
            original_card = self.agent_card
            original_context_builder = getattr(self, "_context_builder", None)

            # 设置动态卡片
            try:
                self.agent_card = self._get_agent_card_from_db(agent_index, request)
                self.handler.agent_card.name = self.agent_card.name
                self.handler.agent_card.description = self.agent_card.description
            except Exception as e:
                return JSONResponse(
                    {"error": f"Failed to get agent card: {str(e)}"}, status_code=404
                )

            # 创建新的上下文构建器实例
            self._context_builder = DynamicContextBuilder(
                original_context_builder, agent_index
            )

            response = await self._handle_requests(request)
            return response
        except Exception as e:
            import traceback

            traceback.print_exc()
            return JSONResponse(
                {
                    "error": "Internal server error",
                    "details": str(e),
                    "type": type(e).__name__,
                },
                status_code=500,
            )
        finally:
            # 安全恢复原始状态
            if original_card is not None:
                self.agent_card = original_card
            if original_context_builder is not None:
                self._context_builder = original_context_builder

    def build(
        self,
        agent_card_url: str = "/.well-known/agent.json",
        rpc_url: str = "/",
        extended_agent_card_url: str = "/agent/authenticatedExtendedCard",
        **kwargs: Any,
    ) -> Starlette:
        """构建应用实例"""
        app = Starlette(**kwargs)
        self.add_routes_to_app(
            app,
            agent_card_url=agent_card_url,
            rpc_url=rpc_url,
            extended_agent_card_url=extended_agent_card_url,
        )
        return app


@click.command()
@click.option("--host", default="localhost")
@click.option("--port", default=10001)
def main(host: str, port: int):
    """启动数据库驱动的A2A服务器"""
    # 初始化数据库

    task_store = InMemoryTaskStore()
    request_handler = DefaultRequestHandler(
        agent_executor=CoreAgentExecutor(0),
        task_store=task_store,
    )
    server = DatabaseA2AStarletteApplication(db, request_handler)
    uvicorn.run(server.build(), host=host, port=port)


if __name__ == "__main__":
    main()

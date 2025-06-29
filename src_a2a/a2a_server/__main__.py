import click
import uvicorn
from a2a.server.agent_execution import AgentExecutor
from a2a.server.apps.starlette_app import A2AStarletteApplication
from a2a.server.request_handlers.default_request_handler import (
    DefaultRequestHandler,
)
from a2a.server.tasks.inmemory_task_store import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
    GetTaskRequest,
    GetTaskResponse,
    SendMessageRequest,
    SendMessageResponse,
)
from fastapi import Request
from typing import Dict, Optional

from core.db.base import DatabaseManager
db = DatabaseManager("postgresql://postgres:postgre@localhost/manager_agent")

# 假设这是您自定义的AgentExecutor
class LifeAgentExecutor(AgentExecutor):
    def __init__(self, agent_index: Optional[str] = None):
        super().__init__()
        self.agent_index = agent_index
        
    async def execute(self, task_input: Any) -> Any:
        # 这里可以根据agent_index执行不同的逻辑
        if self.agent_index:
            return f"Agent {self.agent_index} processed: {task_input}"
        return f"Default agent processed: {task_input}"

class A2ARequestHandler(DefaultRequestHandler):
    """处理Life Agent请求的A2A请求处理器"""
    
    def __init__(self, agent_executor_factory, task_store: InMemoryTaskStore):
        self.agent_executor_factory = agent_executor_factory
        super().__init__(None, task_store)  # 临时传入None，实际使用时动态创建
        
    async def on_get_task(self, request: GetTaskRequest) -> GetTaskResponse:
        # 动态创建带有agent_index的执行器
        agent_index = getattr(request, 'agent_index', None)
        self.agent_executor = self.agent_executor_factory(agent_index)
        return await super().on_get_task(request)

class DynamicAgentApp(A2AStarletteApplication):
    """支持动态agent路径的应用"""
    
    def __init__(self, base_agent_card: AgentCard, http_handler_factory):
        super().__init__(base_agent_card, None)  # 临时传入None
        self.base_card = base_agent_card
        self.http_handler_factory = http_handler_factory
        
    def build(self):
        app = super().build()
        
        # 添加动态agent路径支持
        @app.get("/{agent_index}")
        async def serve_agent(agent_index: str, request: Request):
            # 创建带有agent_index的handler
            handler = self.http_handler_factory(agent_index)

            skill_id = db.fetch_one(AgentCardAndSkill, {"agent_card_id": agent_index}).skill_id

            skill_find = db.fetch_all(Skills, {"id": skill_id})

            skills = [
                AgentSkill(
                    id=skill.id,
                    name=skill.name,
                    description=skill.description,
                    tags=skill.tags,
                    examples=skill.examples,
                ) 
                for skill in skill_find
            ]            

            inputModes_ids = db.fetch_all(AgentCardAndInputModes, {"agent_id": agent_index})
            defaultInputModes = [
                db.fetch_one(InputModes, {"id": inputModes_id}).name
                for inputModes_id in inputModes_ids
            ]

            outputModes_ids = db.fetch_all(AgentCardAndOutputModes, {"agent_id": agent_index})
            defaultOutputModes = [
                db.fetch_one(InputModes, {"id": outputModes_id}).name
                for outputModes_id in outputModes_ids
            ]

            agent_find = db.fetch_all(AgentCard_, {"id": agent_index})
            # 动态创建agent卡片
            agent_card = AgentCard(
                name=agent_find.name,
                description=agent_find.description,
                url=str(request.url),
                version=agent_find.version,
                defaultInputModes=defaultInputModes,
                defaultOutputModes=defaultOutputModes,
                capabilities=AgentCapabilities(
                    inputModes=defaultInputModes,
                    outputModes=defaultOutputModes,
                    streaming=agent_find.streaming,
                ),
                skills=skills,
                examples=agent_card.examples
            )
            
            # 保存当前handler供后续请求使用
            self.http_handler = handler
            return agent_card
            
        return app

@click.command()
@click.option('--host', 'host', default='localhost')
@click.option('--port', 'port', default=10001)
def main(host: str, port: int):
    """启动Life Agent服务器
    
    Args:
        host (str): 服务器主机地址
        port (int): 服务器端口号
    """

    base_agent_card = AgentCard(
        name='',
        description='',
        url='',  # 基础URL会被动态覆盖
        version='',
        defaultInputModes=[],
        defaultOutputModes=[],
        capabilities=AgentCapabilities(
            inputModes=[],
            outputModes=[],
            streaming=True,
        ),
        skills=[],
        examples=[],
    )

    task_store = InMemoryTaskStore()
    
    # 创建工厂函数
    def handler_factory(agent_index: Optional[str] = None):
        executor = LifeAgentExecutor(agent_index)
        return A2ARequestHandler(lambda: executor, task_store)
    
    server = DynamicAgentApp(
        base_agent_card=base_agent_card,
        http_handler_factory=handler_factory
    )
    uvicorn.run(server.build(), host=host, port=port)

if __name__ == '__main__':
    main()
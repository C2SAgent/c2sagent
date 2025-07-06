from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.types import (
    TaskArtifactUpdateEvent,
    TaskState,
    TaskStatus,
    TaskStatusUpdateEvent,
)
from a2a.utils import new_agent_text_message, new_task, new_text_artifact
from typing import Optional, override

from src_a2a.a2a_server.agent import Agent
from core.db.base import DatabaseManager
from model.model_agent import AgentCard, AgentCardAndMcpServer

db = DatabaseManager("postgresql://postgres:postgre@localhost/manager_agent")

class CoreAgentExecutor(AgentExecutor):
    """Test AgentProxy Implementation."""

    def __init__(self, agent_index: int = None):
        self.agent_index = agent_index
        print("============================================")
        print(self.agent_index)
        self.agent_find = db.fetch_one(AgentCard, id=self.agent_index)

        self.mcp_server_id = db.fetch_one(AgentCardAndMcpServer, agent_card_id=agent_index).mcp_server_id
        self.agent = Agent(
            mode="complete",
            token_stream_callback=print,
            mcp_url=f'http://localhost:8000/mcp_client/chat',
            agent_index=self.agent_index,
            mcp_server_id=self.mcp_server_id
        )

    @override
    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        query = context.get_user_input()
        print("===========================================================query")
        print(query)
        task = context.current_task

        if not context.message:
            raise Exception('No message provided')

        if not task:
            task = new_task(context.message)
            await event_queue.enqueue_event(task)

        event = await self.agent.stream(query)
        print("===================================================")
        print(event)
        event_queue.enqueue_event(
            TaskStatusUpdateEvent(
                append=True,
                status=TaskStatus(
                    state=TaskState.working,
                    message=new_agent_text_message(
                        event["data"],
                        task.contextId,
                        task.id,
                    ),
                ),
                final=False,
                contextId=task.contextId,
                taskId=task.id,
            )
        )

    @override
    async def cancel(
        self, context: RequestContext, event_queue: EventQueue
    ) -> None:
        raise Exception('cancel not supported')

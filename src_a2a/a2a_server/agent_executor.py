from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.types import (
    TaskArtifactUpdateEvent,
    TaskState,
    TaskStatus,
    TaskStatusUpdateEvent,
)
from a2a.utils import new_agent_text_message, new_task, new_text_artifact
from typing import override

from agent import Agent
from core.db.base import DatabaseManager

db = DatabaseManager("postgresql://postgres:postgre@localhost/manager_agent")

class LifeAgentExecutor(AgentExecutor):
    """Test AgentProxy Implementation."""

    def __init__(self, agent_index: Optional[str] = None):
        self.agent_index = agent_index
        self.agent_find = db.fetch_one(AgentCard, {"name": "AI Assistant"})
        self.mcp_server_id = db.fetch_one(AgentCardAndMcpServer, {"agent_card_id": self.agent_find.id}).mcp_server_id
        self.agent = Agent(
            mode=self.agent_find.mode,
            token_stream_callback=print,
            mcp_url=f'http://localhost:8000/mcp_client/{self.mcp_server_id}',
        )

    @override
    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        query = context.get_user_input()
        task = context.current_task

        if not context.message:
            raise Exception('No message provided')

        if not task:
            task = new_task(context.message)
            event_queue.enqueue_event(task)



        event = await self.agent.stream(query)
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

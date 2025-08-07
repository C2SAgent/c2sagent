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
from core.db.base_sync import DatabaseManager
from model.model_agent import AgentCard, AgentCardAndMcpServer

from api.apps.agent.config import settings

DATABASE_SYNC_URL = settings.DATABASE_SYNC_URL
db = DatabaseManager(DATABASE_SYNC_URL)


class CoreAgentExecutor(AgentExecutor):
    """Test AgentProxy Implementation."""

    def __init__(self, agent_index: int = None):
        self.agent_index = agent_index

        self.agent_find = db.fetch_one(AgentCard, id=self.agent_index)

        self.mcp_server_id = db.fetch_one(
            AgentCardAndMcpServer, agent_card_id=agent_index
        ).mcp_server_id

    # TODO: 待完成
    #
    @override
    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:

        print("=========================动态self.mcp_server_id")
        print(self.mcp_server_id)
        print(self.agent_index)

        self.agent = Agent(
            mode="complete",
            token_stream_callback=print,
            mcp_url=f"http://localhost:8000/app_mcp/ask_mcp",
            agent_index=self.agent_index,
            mcp_server_id=self.mcp_server_id,
        )

        query = context.get_user_input()
        task = context.current_task

        if not context.message:
            raise Exception("No message provided")

        if not task:
            task = new_task(context.message)
            await event_queue.enqueue_event(task)

        event = await self.agent.completion(query)

        print("=================================query")
        print(query)

        await event_queue.enqueue_event(
            TaskStatusUpdateEvent(
                append=True,
                status=TaskStatus(
                    state=TaskState.working,
                    message=new_agent_text_message(
                        event,
                        task.contextId,
                        task.id,
                    ),
                ),
                final=False,
                contextId=task.contextId,
                taskId=task.id,
            )
        )

    # @override
    # async def execute(
    #     self,
    #     context: RequestContext,
    #     event_queue: EventQueue,
    # ) -> None:
    #     query = context.get_user_input()
    #     task = context.current_task

    #     if not context.message:
    #         raise Exception('No message provided')

    #     if not task:
    #         task = new_task(context.message)
    #         await event_queue.enqueue_event(task)

    #     async for event in self.agent.stream(query):
    #         if event['is_task_complete']:
    #             await event_queue.enqueue_event(
    #                 TaskArtifactUpdateEvent(
    #                     append=False,
    #                     contextId=task.contextId,
    #                     taskId=task.id,
    #                     lastChunk=True,
    #                     artifact=new_text_artifact(
    #                         name='current_result',
    #                         description='Result of request to agent.',
    #                         text=event['content'],
    #                     ),
    #                 )
    #             )
    #             await event_queue.enqueue_event(
    #                 TaskStatusUpdateEvent(
    #                     status=TaskStatus(state=TaskState.completed),
    #                     final=True,
    #                     contextId=task.contextId,
    #                     taskId=task.id,
    #                 )
    #             )
    #         elif event['require_user_input']:
    #             await event_queue.enqueue_event(
    #                 TaskStatusUpdateEvent(
    #                     status=TaskStatus(
    #                         state=TaskState.input_required,
    #                         message=new_agent_text_message(
    #                             event['content'],
    #                             task.contextId,
    #                             task.id,
    #                         ),
    #                     ),
    #                     final=True,
    #                     contextId=task.contextId,
    #                     taskId=task.id,
    #                 )
    #             )
    #         else:
    #             await event_queue.enqueue_event(
    #                 TaskStatusUpdateEvent(
    #                     append=True,
    #                     status=TaskStatus(
    #                         state=TaskState.working,
    #                         message=new_agent_text_message(
    #                             event['content'],
    #                             task.contextId,
    #                             task.id,
    #                         ),
    #                     ),
    #                     final=False,
    #                     contextId=task.contextId,
    #                     taskId=task.id,
    #                 )
    #             )

    @override
    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise Exception("cancel not supported")

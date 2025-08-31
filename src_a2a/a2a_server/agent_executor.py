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

from core.llm.llm_client import LLMClient
from src_a2a.a2a_server.agent import Agent
from core.db.base_sync import DatabaseManager
from model.model_agent import AgentCard, AgentCardAndMcpServer

from api.apps.agent.config import settings

DATABASE_SYNC_URL = settings.DATABASE_SYNC_URL
db = DatabaseManager(DATABASE_SYNC_URL)


class CoreAgentExecutor(AgentExecutor):
    """Test AgentProxy Implementation."""

    def __init__(self, agent_index: int = None):

        self.agent_find = None
        self.mcp_server_find = None
        self.mcp_server_id = None

        self.agent_index = agent_index

        if self.agent_index != 0:
            self.agent_find = db.fetch_one(AgentCard, id=self.agent_index)

        if self.agent_find:
            self.mcp_server_find = db.fetch_one(
                AgentCardAndMcpServer, agent_card_id=agent_index
            )

        if self.mcp_server_find:
            self.mcp_server_id = self.mcp_server_find.mcp_server_id

    @override
    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:

        if not self.agent_find:
            task = context.current_task

            if not context.message:
                raise Exception("No message provided")

            if not task:
                task = new_task(context.message)
                await event_queue.enqueue_event(task)
            await event_queue.enqueue_event(
                TaskStatusUpdateEvent(
                    status=TaskStatus(
                        state=TaskState.completed,
                        message=new_agent_text_message(
                            "Agent not found for this user",
                            task.contextId,
                            task.id,
                        ),
                    ),
                    final=True,
                    contextId=task.contextId,
                    taskId=task.id,
                )
            )
        elif not self.mcp_server_id:
            task = context.current_task
            query = context.get_user_input()

            if not context.message:
                raise Exception("No message provided")

            if not task:
                task = new_task(context.message)
                await event_queue.enqueue_event(task)
                
            
            print("Agent================================")
            print(self.agent_find.llm_name)
            print(self.agent_find.llm_url)
            print(self.agent_find.llm_key)
            llm_client = LLMClient()
            async for event in llm_client.get_stream_response_reasion_and_content(
                messages=[{"role": "system", "content": f"这是对你的描述：\n\n{self.agent_find.description}"}, {"role": "user", "content": query}],
                llm_url=self.agent_find.llm_url,
                api_key=self.agent_find.llm_key,
                model_name="deepseek-reasoner"
                if self.agent_find.llm_name == "deepseek"
                else self.agent_find.llm_name,
            ):
                await event_queue.enqueue_event(
                    TaskStatusUpdateEvent(
                        status=TaskStatus(
                            state=TaskState.working,
                            message=new_agent_text_message(
                                event["content"],
                                task.contextId,
                                task.id,
                            ),
                        ),
                        final=False,
                        contextId=task.contextId,
                        taskId=task.id,
                    )
            )            
        else:
            self.agent = Agent(
                mode="complete",
                token_stream_callback=print,
                mcp_url=f"http://localhost:8000/app_mcp/ask_mcp_streaming",
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

            async for event in self.agent.stream(query):
                if event["is_task_complete"]:
                    await event_queue.enqueue_event(
                        TaskStatusUpdateEvent(
                            status=TaskStatus(
                                state=TaskState.completed,
                                message=new_agent_text_message(
                                    event["content"],
                                    task.contextId,
                                    task.id,
                                ),
                            ),
                            final=True,
                            contextId=task.contextId,
                            taskId=task.id,
                        )
                    )
                elif event["require_user_input"]:
                    await event_queue.enqueue_event(
                        TaskStatusUpdateEvent(
                            status=TaskStatus(
                                state=TaskState.input_required,
                                message=new_agent_text_message(
                                    event["content"],
                                    task.contextId,
                                    task.id,
                                ),
                            ),
                            final=True,
                            contextId=task.contextId,
                            taskId=task.id,
                        )
                    )
                else:
                    await event_queue.enqueue_event(
                        TaskStatusUpdateEvent(
                            append=True,
                            status=TaskStatus(
                                state=TaskState.working,
                                message=new_agent_text_message(
                                    event["content"],
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
    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise Exception("cancel not supported")

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

from agent_executor import LifeAgentExecutor

class A2ARequestHandler(DefaultRequestHandler):
    """A2A Request Handler for the Life Agent."""

    def __init__(
        self, agent_executor: AgentExecutor, task_store: InMemoryTaskStore
    ):
        super().__init__(agent_executor, task_store)

    async def on_get_task(self, request: GetTaskRequest) -> GetTaskResponse:
        return await super().on_get_task(request)

    # async def on_message_send(
    #     self, request: SendMessageRequest
    # ) -> SendMessageResponse:
    #     return await super().on_message_send(request)


@click.command()
@click.option('--host', 'host', default='localhost')
@click.option('--port', 'port', default=10001)
def main(host: str, port: int):
    """Start the Life Agent server.

    This function initializes the Life Agent server with the specified host and port.
    It creates an agent card with the agent's name, description, version, and capabilities.

    Args:
        host (str): The host address to run the server on.
        port (int): The port number to run the server on.
    """  # noqa: E501
    skill = AgentSkill(
        id='answer_detial_about_Life',
        name='Answer any information about Life',
        description='The agent that can meet daily needs, including features such as a calendat, weather, and more.',  # noqa: E501
        tags=['Life'],
        examples=['How is the weather tomorrow?', 'Check today\'s calendar for me'],
    )

    agent_card = AgentCard(
        name='Life Agent',
        description='An agent that can meet daily needs, including features such as a calendat, weather, and more',  # noqa: E501
        url=f'http://{host}:{port}/',
        version='1.0.0',
        defaultInputModes=['text'],
        defaultOutputModes=['text'],
        capabilities=AgentCapabilities(
            inputModes=['text'],
            outputModes=['text'],
            streaming=True,
        ),
        skills=[skill],
        # authentication=AgentAuthentication(schemes=['public']),
        examples=['How is the weather tomorrow?', 'Check today\'s calendar for me'],
    )

    task_store = InMemoryTaskStore()
    request_handler = A2ARequestHandler(
        agent_executor=LifeAgentExecutor(),
        task_store=task_store,
    )

    server = A2AStarletteApplication(
        agent_card=agent_card, http_handler=request_handler
    )
    uvicorn.run(server.build(), host=host, port=port)

if __name__ == '__main__':
    main()

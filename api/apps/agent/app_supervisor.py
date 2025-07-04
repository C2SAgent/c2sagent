import asyncio
import json
from typing import Literal


import asyncclick as click
import colorama
import requests
from src_a2a.a2a_client.agent import Agent


@click.command()
@click.option('--host', 'host', default='localhost')
@click.option('--port', 'port', default=8000)
@click.option('--mode', 'mode', default='streaming')
# @click.option('--question', 'question', required=True)
async def a_main(
    host: str,
    port: int,
    mode: Literal['completion', 'streaming'],
    # question: str,
):
    """Main function to run the A2A Repo Agent client.

    Args:
        host (str): The host address to run the server on.
        port (int): The port number to run the server on.
        mode (Literal['completion', 'streaming']): The mode to run the server on.
        question (str): The question to ask the Agent.
    """  # noqa: E501

    url = "http://localhost:10001/ask-agent"

    headers = {
        "Content-Type": "application/json"
    }
    # Create the request payload
    payload = {
        "host": "localhost",
        "port": 10001,
        "mode": "completion",  # or "completion"
        "user_id": "123",     # replace with actual user_id
        "question": "查询一下武汉的天气"
    }

    try:
        # Make the POST request
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        # Check if the request was successful
        if response.status_code == 200:
            print("Response from agent:", response.json()["result"])
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

    
    # agent = Agent(
    #     mode='stream',
    #     token_stream_callback=None,
    #     agent_urls=[f'http://{host}:{port}/'],
    # )
    # question = "查询一下武汉的天气"
    # result = await agent.stream(question)
    # print(result)



def main() -> None:
    """Main function to run the A2A Repo Agent client."""
    asyncio.run(a_main())


if __name__ == '__main__':
    main()

import aiohttp
import asyncio
import json


async def register_user():
    url = "http://localhost:8000/agent/list"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer your_token_here",  # 替换为实际token
    }
    data = {
        "name": "test88",
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                print(f"Status: {response.status}")
                print(f"Response: {await response.text()}")

                if response.status == 200:
                    result = await response.json()
                    print("Registration successful!")
                    print(f"User created: {result['name']}")
                else:
                    error_detail = await response.json()
                    print(f"Error: {error_detail.get('detail', 'Unknown error')}")

    except aiohttp.ClientError as e:
        print(f"Request failed: {str(e)}")
    except json.JSONDecodeError:
        print("Invalid JSON response")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")


# 运行异步函数
asyncio.run(register_user())

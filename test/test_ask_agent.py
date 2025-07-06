import requests
import json

# # Define the API endpoint URL
# url = "http://localhost:8000/chat/ask-agent"

# # Set headers
# headers = {
#     "Content-Type": "application/json"
# }

# try:
#     # Make the POST request
#     response = requests.get(url, headers=headers, params={"question": "查一下武汉的天气"})
    
#     # Check if the request was successful
#     if response.status_code == 200:
#         print("Response from agent:", response.json()["result"])
#     else:
#         print(f"Error: {response.status_code} - {response.text}")
# except requests.exceptions.RequestException as e:
#     print(f"Request failed: {e}")
    
url = "http://localhost:8000/mcp_client/chat"

# Set headers
headers = {
    "Content-Type": "application/json"
}

try:
    # Make the POST request
    response = requests.post(url, headers=headers, json={"query": "查一下武汉的天气", "mcp_server_id": 3, "agent_id": 8})
    
    # Check if the request was successful
    if response.status_code == 200:
        print("Response from agent:", response.json()["result"])
    else:
        print(f"Error: {response.status_code} - {response.text}")
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")

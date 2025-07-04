import requests
import json

# Define the API endpoint URL
url = "http://localhost:10001/ask-agent"

# Create the request payload
payload = {
    "host": "localhost",
    "port": 10001,
    "mode": "streaming",  # or "completion"
    "user_id": "123",     # replace with actual user_id
    "question": "查一下武汉的天气"
}

# Set headers
headers = {
    "Content-Type": "application/json"
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
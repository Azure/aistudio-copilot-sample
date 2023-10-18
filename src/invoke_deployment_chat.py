import requests
import json
import os

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {os.getenv('DEPLOYMENT_KEY')}",
    "Accept": "text/event-stream",
}

response = requests.post(
    os.getenv("DEPLOYMENT_SCORING_URL"),
    headers=headers,
    json={
        "messages": [{"role": "user", "content": "What tent has the highest rainfly rating?"}],
        "stream": True,
    },
    stream=True
)
print(response.headers)
for item in response.iter_lines(chunk_size=None):
    print(item)
    print("\n")

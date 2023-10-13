import requests
import json
import os

headers = {
    "Content-Type": "application/json",
    "Accept": "text/event-stream",
}

response = requests.post(
    "http://127.0.0.1:5001/score",
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

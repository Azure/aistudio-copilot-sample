import os
import json
from typing import List

file_name = "chat_history.json"

def read_chat_history() -> List:
    if not os.path.exists(file_name):
        return []
 
    f = open(file_name)
    chat_history = json.load(f)
    return chat_history

def update_chat_history(question: str, answer: str):
    chat_history = read_chat_history()
    chat_history.append({"role": "user", "content": question })
    chat_history.append({"role": "assistant", "content": answer })

    json_object = json.dumps(chat_history, indent=4)
    with open(file_name, "w") as outfile:
        outfile.write(json_object)

def delete_chat_history():
    os.remove(file_name)

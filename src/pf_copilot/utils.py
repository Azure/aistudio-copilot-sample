import os
from typing import List
from langchain.memory import ConversationBufferMemory
from promptflow.connections import AzureOpenAIConnection, CognitiveSearchConnection

def create_cp_user_content(question: str):
    cp_message = {}
    cp_message["content"] = question
    cp_message["role"] = "user"
    return cp_message

def create_cp_assistant_content(answer: str):
    cp_message = {}
    cp_message["content"] = answer
    cp_message["role"] = "assistant" # the term "assistant" is from Chat Protocol doc
    return cp_message

# Convert from PromptFlow to Chat Protocol
def convert_chat_history_pf_to_cp(pf_chat_history: List[dict], cp_messages: List[dict]):
    for pf_item in pf_chat_history:
        cp_messages.append(create_cp_user_content(pf_item["inputs"]["question"]))
        cp_messages.append(create_cp_assistant_content(pf_item["outputs"]["answer"]))

# Convert from Chat Protocol to LangChain
def convert_chat_history_cp_to_lc(cp_messages: List[dict], lc_memory: ConversationBufferMemory):
    lc_memory.clear()
    for cp_message in cp_messages:
        if cp_message["role"] == "user":
            lc_memory.chat_memory.add_user_message(cp_message["content"])
        elif cp_message["role"] == "assistant":
            lc_memory.chat_memory.add_ai_message(cp_message["content"])

def print_pf_chat_history(chat_history: List[dict]):
    for item in chat_history:
        print(f"Question: {item['inputs']['question']}")
        print(f"Answer: {item['outputs']['answer']}")

def set_aoai_environment(aoai_connection: AzureOpenAIConnection):
    try:
        import openai
    except ImportError:
        raise Exception("OpenAI SDK not installed. Please install it using `pip install openai`")

    openai.api_type = "azure"
    openai.api_key = aoai_connection.api_key
    openai.api_version = aoai_connection.api_version
    openai.api_base = aoai_connection.api_base
    os.environ["OPENAI_API_TYPE"] = "azure"
    os.environ["OPENAI_API_KEY"] = aoai_connection.api_key
    os.environ["OPENAI_API_VERSION"] = aoai_connection.api_version
    os.environ["OPENAI_API_BASE"] = aoai_connection.api_base

def set_acs_environment(acs_connection: CognitiveSearchConnection):
    os.environ["AZURE_COGNITIVE_SEARCH_TARGET"] = acs_connection.api_base
    os.environ["AZURE_COGNITIVE_SEARCH_KEY"] = acs_connection.api_key

import os, pathlib

from typing import Any, List
from langchain import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.chat_models import AzureChatOpenAI
from langchain.memory import ConversationBufferMemory
from azure.ai.generative.index import get_langchain_retriever_from_index

def setup_credentials():
    # Azure OpenAI credentials
    import openai
    openai.api_type = os.environ["OPENAI_API_TYPE"]
    openai.api_key = os.environ["OPENAI_API_KEY"]
    openai.api_version = os.environ["OPENAI_API_VERSION"]
    openai.api_base = os.environ["OPENAI_API_BASE"]

    # Azure Cognitive Search credentials
    os.environ["AZURE_COGNITIVE_SEARCH_TARGET"] = os.environ["AZURE_AI_SEARCH_ENDPOINT"]
    os.environ["AZURE_COGNITIVE_SEARCH_KEY"] = os.environ["AZURE_AI_SEARCH_KEY"]

def convert_chat_history_cp_to_lc(cp_messages: List[dict], lc_memory: ConversationBufferMemory):
    lc_memory.clear()
    for cp_message in cp_messages:
        if cp_message["role"] == "user":
            lc_memory.chat_memory.add_user_message(cp_message["content"])
        elif cp_message["role"] == "assistant":
            lc_memory.chat_memory.add_ai_message(cp_message["content"])

async def chat_completion(messages: list[dict], stream: bool = False,
    session_state: Any = None, context: dict[str, Any] = {}):
    setup_credentials()

    # extra question from chat history messages
    question = messages[-1]["content"]
    # convert chat history messages into memory
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        input_key="question",
        return_messages=True,
    )
    convert_chat_history_cp_to_lc(messages[:-1], memory)

    llm = AzureChatOpenAI(
        deployment_name=os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT"],
        model_name=os.environ["AZURE_OPENAI_CHAT_MODEL"],
        temperature=context.get('temperature', 0.7)
    )

    template = """
    System:
    You are an AI assistant helping users with queries related to outdoor outdooor/camping gear and clothing.
    Use the following pieces of context to answer the questions about outdoor/camping gear and clothing as completely, correctly, and concisely as possible.

    ---

    {chat_history}

    ---

    {context}

    ---

    Question: {question}

    Answer:"
    """

    prompt_template = PromptTemplate(
        template=template,
        input_variables=[
            "context",
            "chat_history",
            "question"
        ],
    )

    # convert MLIndex to a langchain retriever
    search_index_folder = os.getenv("AZURE_AI_SEARCH_INDEX_NAME") + "-mlindex"
    search_index_path = os.path.join(pathlib.Path(__file__).parent.resolve(), search_index_folder)
    index_langchain_retriever = get_langchain_retriever_from_index(search_index_path)

    qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=index_langchain_retriever,
        return_source_documents=True,
        chain_type_kwargs={
            "prompt": prompt_template,
        }
    )
    qa.combine_documents_chain.memory = memory

    response = qa({ "question": question, "query": question })
    return {
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": response["result"]
            },
            "context": question,
        }]
    }

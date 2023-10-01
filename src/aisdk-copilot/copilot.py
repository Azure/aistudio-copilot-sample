# this enables type hints on Python < 3.9
from __future__ import annotations

import os
import openai
import jinja2
import asyncio

from azure.core.credentials import AzureKeyCredential
from azure.search.documents.aio import SearchClient

templateLoader = jinja2.FileSystemLoader(searchpath="./")
templateEnv = jinja2.Environment(loader=templateLoader)
system_message_template = templateEnv.get_template("system-message.jinja2")

async def get_context(query, num_docs=5):
    #  retrieve documents relevant to the user's question from Cognitive Search
    search_client = SearchClient(
        endpoint=os.environ["AZURE_COGNITIVE_SEARCH_TARGET"],
        credential=AzureKeyCredential(os.environ["AZURE_COGNITIVE_SEARCH_KEY"]),
        index_name=os.environ["AZURE_SEARCH_INDEX_NAME"])

    context = ""

    async with search_client:
        # generate a vector embedding of the user's question
        embedding = await openai.Embedding.acreate(
            model=os.environ["AZURE_OPENAI_EMBEDDING_MODEL"],
            deployment_id=os.environ["AZURE_OPENAI_EMBEDDING_DEPLOYMENT"],
            input=query)
        query_vector = embedding["data"][0]["embedding"]
            
        # use the vector embedding to do a vector search on the index
        results = await search_client.search(query, vector=query_vector, 
            top=num_docs, vector_fields="content_vector_open_ai")

        async for result in results:
            context += f"\n>>> From: {result['sourcepage']}\n{result['content']}"      

    return context
    
async def chat(messages: list[dict], stream: bool = False, 
    session_state: Any = None, extra_args: dict[str, Any] = {}):
    
    # get search documents for the last user message in the conversation
    user_message = messages[-1]["content"]
    context = await get_context(user_message, extra_args.get("num_retrieved_docs", 5))    
    
    # add retrieved documents as context to the system prompt 
    system_message = system_message_template.render(context=context)
    messages.insert(0, {"role":"system","content": system_message})
    
    # call Azure OpenAI with the system prompt and user's question
    response = openai.ChatCompletion.create(
        engine=os.environ.get("AZURE_OPENAI_CHAT_DEPLOYMENT"),
        messages=messages, temperature=extra_args.get("temperature", 0.7),
        max_tokens=800)
    
    # add context in the returned response
    response.choices[0]['extra_args'] = {'context': context}
    return response

if __name__ == "__main__":
    # Set up environment variables by using values from the project
    # In production these would be variables that are set on the docker container
    from azure.ai.generative import AIClient
    from azure.identity import DefaultAzureCredential
    
    client = AIClient.from_config(DefaultAzureCredential())
    client.get_default_aoai_connection().set_current_environment()
    client.connections.get("Default_CognitiveSearch").set_current_environment()
    
    # TODO: unable to get code for this index
    # index = client.mlindexes.get(name="product-info-cog-search-index", label="latest")
    os.environ["AZURE_SEARCH_INDEX_NAME"] = "product-info-index-test1"
    
    # TODO: set these automatically using client.deployment.get_default_chat etc.
    os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT"] = "gpt-35-turbo-16k-0613"
    os.environ["AZURE_OPENAI_EMBEDDING_MODEL"] = "text-embedding-ada-002"
    os.environ["AZURE_OPENAI_EMBEDDING_DEPLOYMENT"] = "text-ada-embedding-002-2"

    import platform
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            
    result = asyncio.run(chat([{"role": "user", "content": "which tent has the highest waterproof rating?"}]))
    print(result['choices'][0])
    

    
    
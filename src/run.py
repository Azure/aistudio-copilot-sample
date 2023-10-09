# enable type annotation syntax on Python versions earlier than 3.9
from __future__ import annotations

def init_environment(self):
    import os

    # Set up environment variables by using values from the project
    # In production these would be variables that are set on the docker container
    from azure.ai.generative import AIClient
    from azure.identity import DefaultAzureCredential
    
    client = AIClient.from_config(DefaultAzureCredential())
    client.get_default_aoai_connection().set_current_environment()
    client.connections.get("Default_CognitiveSearch").set_current_environment()
        
    # TODO: set these automatically by calling into AIClient and retrieving values
    os.environ["AZURE_SEARCH_INDEX_NAME"] = "product-info-index-test1"
    os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT"] = "gpt-35-turbo-16k-0613"
    os.environ["AZURE_OPENAI_EVALUATION_DEPLOYMENT"] = "gpt-35-turbo-16k-0613"
    os.environ["AZURE_OPENAI_EMBEDDING_MODEL"] = "text-embedding-ada-002"
    os.environ["AZURE_OPENAI_EMBEDDING_DEPLOYMENT"] = "text-ada-embedding-002-2"

# for demo purposes, add method to AIClient
from azure.ai.generative import AIClient
AIClient.set_environment_variables = init_environment

    
# Run a single chat message through one of the co-pilot implementations
if __name__ == "__main__":
    import pathlib
    import sys
    #sys.path.append(pathlib.Path(__file__).parent.resolve())
    
    # configure asyncio
    import asyncio
    import platform

    # workaround for a bug on windows
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--question", help="The question to ask the copilot", type=str)
    parser.add_argument("--implementation", help="The implementation to use", type=str)
    parser.add_argument("--use-semantic-kernel", help="Use semantic kernel implementation", action='store_true')
    args = parser.parse_args()
    
    if args.implementation:
        if args.implementation == "promptflow":
            from copilot_promptflow.chat import chat_completion
        elif args.implementation == "semantickernel":
            from copilot_semantickernel.chat import chat_completion
        elif args.implementation == "langchain":
            from copilot_langchain.chat import chat_completion
        elif args.implementation == "aisdk":
            from copilot_aisdk.chat import chat_completion
    else:
        from copilot_aisdk.chat import chat_completion
            
    
    # set environment variables before importing the co-pilot code
    from azure.ai.generative import AIClient
    from azure.identity import DefaultAzureCredential
    
    client = AIClient.from_config(DefaultAzureCredential())
    client.set_environment_variables()
    
    question = "which tent has the highest waterproof rating?"
    if args.question:
        question = args.question
           
    # Call the async chat function with a single question and print the response
    result = asyncio.run(
        chat_completion([{"role": "user", "content": question}])
    )
    print(result)
    
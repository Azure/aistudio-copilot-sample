# enable type annotation syntax on Python versions earlier than 3.9
from __future__ import annotations

# set environment variables before importing any other code (in particular the openai module)
from dotenv import load_dotenv
load_dotenv()
    
    
# Run a single chat message through one of the co-pilot implementations
if __name__ == "__main__":
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
            
    question = "which tent is the most waterproof?"
    if args.question:
        question = args.question
           
    # Call the async chat function with a single question and print the response
    result = asyncio.run(
        chat_completion([{"role": "user", "content": question}])
    )
    print(result)
    
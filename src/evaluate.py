import os
import json
from pprint import pprint

# set environment variables before the openai SDK gets imported
from dotenv import load_dotenv
load_dotenv()

from azure.identity import DefaultAzureCredential
from azure.ai.generative import AIClient
from azure.ai.generative.evaluate import evaluate

# TEMP: wrapper around chat completion function until chat_completion protocol is supported
def copilot_qna(question, chat_completion_fn):
    # Call the async chat function with a single question and print the response    
    import asyncio
    import platform
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    result = asyncio.run(
        chat_completion_fn([{"role": "user", "content": question}])
    )
    response = result['choices'][0]
    return {
        "question": question,
        "answer": response["message"]["content"],
        "context": response["context"]
    }
 
 # Define helper methods
def load_jsonl(path):
    with open(path, "r") as f:
        return [json.loads(line) for line in f.readlines()]

def run_evaluation(chat_completion_fn, name, dataset_path):
    # Evaluate the default vs the improved system prompt to see if the improved prompt
    # performs consistently better across a larger set of inputs
    path = os.path.join(os.getcwd() + dataset_path)
    dataset = load_jsonl(path)
    
    # temp: generate a single-turn qna wrapper over the chat completion function
    qna_fn = lambda question: copilot_qna(question, chat_completion_fn)
    
    client = AIClient.from_config(DefaultAzureCredential())
    result = evaluate(
        evaluation_name=name,
        asset=qna_fn,
        data=dataset,
        task_type="qa",
        prediction_data="answer",
        truth_data="truth",
        metrics_config={
            "openai_params": {
                "api_version": "2023-05-15",
                "api_base": os.getenv("OPENAI_API_BASE"),
                "api_type": "azure",
                "api_key": os.getenv("OPENAI_API_KEY"),
                "deployment_id": os.getenv("AZURE_OPENAI_EVALUATION_DEPLOYMENT")
            },
            "questions": "question",
            "contexts": "context",
        },
        tracking_uri=client.tracking_uri,
    )
    return result

if __name__ == "__main__": 
    from copilot_aisdk import chat
    results = run_evaluation(chat.chat_completion, "test_aisdk_copilot", "/src/evaluation_dataset.jsonl")
    print(results)

import os
import json
import pytest

from pprint import pprint

from azure.identity import DefaultAzureCredential
from azure.ai.generative import AIClient
from azure.ai.generative.evaluate import evaluate
  
from run import init_environment
from aisdk_copilot import copilot

# Test results are stored here
gpt_groundedness_score : float
gpt_coherence_score : float
gpt_similarity_score : float

evaluation_results : any

# Define helper methods
def load_jsonl(path):
    with open(path, "r") as f:
        return [json.loads(line) for line in f.readlines()]

# TEMP: wrapper around chat completion function until chat_completion protocol is supported
def copilot_qna(question):
    # Call the async chat function with a single question and print the response    
    import asyncio
    import platform
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    result = asyncio.run(
        copilot.chat_completion([{"role": "user", "content": question}])
    )
    response = result['choices'][0]
    return {
        "question": question,
        "answer": response["message"]["content"],
        "context": response["extra_args"]["context"]
    }
    
def run_evaluation():
    # set environment variables to point at current Azure AI Project
    init_environment()
    
    # Evaluate the default vs the improved system prompt to see if the improved prompt
    # performs consistently better across a larger set of inputs
    path = os.path.join(os.getcwd() + "/src/evaluation_dataset.jsonl")
    data = load_jsonl(path)

    ai_client = AIClient.from_config(DefaultAzureCredential())      
    result = evaluate(
        evaluation_name="test_aisdk_copilot",
        asset=copilot_qna,
        data=data,
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
        tracking_uri=ai_client.tracking_uri,
    )
    
    global evaluation_results
    evaluation_results = result

@pytest.fixture(scope="session", autouse=True)
def run_before_any_test():
    run_evaluation()
    
def get_metric_average(metric_name):    
    # metrics format is e.g.: ['3', '5', '5', '5', '5', '4', '3', '5', '5', '5', '5', '5', '1']
    metrics_array_str = evaluation_results["artifacts"][metric_name]
    
    # convert to array of floats
    metrics_array_float = [float(value) for value in metrics_array_str]
    average = sum(metrics_array_float) / len(metrics_array_float)
    
    print(f"{metric_name}: average {average}")
    return average
    
def test_gpt_groundedness_atleast4():
    assert(get_metric_average("gpt_groundedness") >= 4)

def test_gpt_similarity_atleast4():
    assert(get_metric_average("gpt_similarity") >= 4)

def test_gpt_relevance_atleast4():
    assert(get_metric_average("gpt_relevance") >= 4)
        
def test_gpt_coherence_atleast4():
    assert(get_metric_average("gpt_coherence") >= 4)
    
def test_gpt_fluency_atleast4():
    assert(get_metric_average("gpt_fluency") >= 4)
    
if __name__ == "__main__": 
    run_evaluation()
    test_gpt_groundedness_atleast4()
    #pprint(evaluation_results)
    
    #print("hello!")
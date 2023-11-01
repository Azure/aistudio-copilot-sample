# enable type annotation syntax on Python versions earlier than 3.9
from __future__ import annotations
import os

from promptflow import PFClient
from azure.ai.ml.constants._common import AZUREML_RESOURCE_PROVIDER, RESOURCE_ID_FORMAT
    
async def chat_completion(messages: list[dict], stream: bool = False, 
    session_state: Any = None, context: dict[str, Any] = {}):

    pf_client = PFClient(config={"connection.provider": "azureml:"
                + RESOURCE_ID_FORMAT.format(
                    os.environ["AZURE_SUBSCRIPTION_ID"], os.environ["AZURE_RESOURCE_GROUP"], AZUREML_RESOURCE_PROVIDER, os.environ["AZURE_AI_PROJECT_NAME"]
                )})
    
    inputs = {"chat_history": messages[:-1], "question": messages[-1], "customerId": 2}  
    result = pf_client.test(flow="src/copilot_promptflow", inputs=inputs)
    answer = result['answer']
    
    # convert generator to text if the caller didn't ask to stream
    if not stream:
        answer = ""
        for value in result['answer']:
            answer += value
            
    return {
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": answer
            },
            "context": result['context']
        }]
    }
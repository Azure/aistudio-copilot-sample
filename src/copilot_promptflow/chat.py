# enable type annotation syntax on Python versions earlier than 3.9
from __future__ import annotations

from promptflow import PFClient
    
async def chat_completion(messages: list[dict], stream: bool = False, 
    session_state: Any = None, extra_args: dict[str, Any] = {}):

    pf_client = PFClient()  
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
            "extra_args": {
                "context": result['context']
            }
        }]
    }
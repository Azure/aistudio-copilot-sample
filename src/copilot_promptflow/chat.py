# enable type annotation syntax on Python versions earlier than 3.9
from __future__ import annotations
from pathlib import Path
import os

from promptflow import PFClient

from streaming_utils import contruct_streamed_pf_response


def _get_connection_provider_id():
    return (
        "azureml://subscriptions/{}/resourceGroups/{}/"
        "providers/Microsoft.MachineLearningServices/workspaces/{}"
    ).format(os.getenv("AZURE_SUBSCRIPTION_ID"), os.getenv("AZURE_RESOURCE_GROUP"), os.getenv("AZURE_AI_PROJECT_NAME"))


async def chat_completion(messages: list[dict], stream: bool = False,
    session_state: any = None, context: dict[str, any] = {}):

    pf_client = PFClient(
        config={
            "connection.provider": _get_connection_provider_id(),
        }
    )

    inputs = {"chat_history": messages[:-1], "question": messages[-1], "customerId": 2}
    result = pf_client.test(flow=str(Path(__file__).parent.resolve()), inputs=inputs)
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
                "context": {
                    "documents": result['context']
                },
            }],
            "object": "chat.completion"
        }
    else:
        return contruct_streamed_pf_response(result, session_state)
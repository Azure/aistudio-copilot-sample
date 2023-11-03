from typing import Any, Dict

def add_context_to_streamed_response(response, context):
    first_resp = next(response)
    first_resp.choices[0]["delta"]["context"] = context
    yield first_resp
    yield from response


def create_pf_token_response(result):
    for token in result["answer"]:
        yield {
            "choices": [
                {
                    "delta": {
                        "content": token,
                    },
                    "finish_reason": None,
                    "index": 0
                }
            ],
            "object": "chat.completion.chunk",
        }


def contruct_streamed_pf_response(result: Dict, session_state: Any = None):
    yield {
        "choices": [
            {
                "delta": {
                    "role": "assistant",
                    "context": {
                        "documents": result["context"],
                    },
                    "session_state": session_state,
                },
                "finish_reason": None,
                "index": 0
            }
        ],
        "object": "chat.completion.chunk"
    }
    yield from create_pf_token_response(result)
    yield {
        "choices": [
            {
                "delta": {},
                "finish_reason": "stop",
                "index": 0
            }
        ],
        "object": "chat.completion.chunk"
    }


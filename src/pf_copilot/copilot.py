# TODO: David?

from promptflow import load_pf

async def chat_completion(messages: list[dict], stream: bool = False, 
    session_state: Any = None, extra_args: dict[str, Any] = {}):

    promptflow = load_pf(".")
    result = promptflow(messages[:-1], messages[-1])
    return result
    
    
    
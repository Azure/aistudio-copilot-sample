import os
import openai
import jinja2
import load_dotenv

from azure.search.documents.aio import SearchClient

templateLoader = jinja2.FileSystemLoader(searchpath="./")
templateEnv = jinja2.Environment(loader=templateLoader)
system_message_template = templateEnv.get_template("system-message.jinja2")

async def chat(messages: List[dict], stream: bool = False, 
    session_state: Any = None, extra_args: Dict[str, Any] = {}):
    
    # retrieve documents relevant to the user's question from Cognitive Search
    search_client = SearchClient()
    response = await self.search_client.search(question, top_k=max_retrieved_docs)

    context = "\n".join([async for doc in response.documents])

    actual_meta_prompt = extra_args.get("meta_prompt", meta_prompt)
        
    # add retrieved documents as context to the system prompt 
    system_message = system_message_template.render(context=context)
    messages.insert[0, {"role":"system","content": system_message}]
    
    # call Azure OpenAI with the system prompt and user's question
    response = openai.ChatCompletion.create(
        engine=os.environ.get("DEFAULT_CHAT_DEPLOYMENT"),
        messages=messages, temperature=extra_args.get("temperature", 0.7),
        max_tokens=800)
    
    return response

if __name__ == "__main__":
    asyncio.run(chat({"user: which tent is the most waterproof?"}))
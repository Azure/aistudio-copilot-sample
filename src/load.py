import os
import asyncio

# set environment variables before the openai SDK gets imported
from dotenv import load_dotenv
load_dotenv()

from azure.ai.generative import AIClient

from azure.identity import ManagedIdentityCredential
from azure.ai.generative import AIClient

from copilot_aisdk.chat import chat_completion

# TODO: send these from the deploy client
def set_environment_variables():
    os.environ['AZURE_AI_SEARCH_ENDPOINT'] = os.environ['AZURE_COGNITIVE_SEARCH_TARGET']
    os.environ['AZURE_COGNITIVE_SEARCH_KEY'] = os.environ['AZURE_COGNITIVE_SEARCH_KEY']
    os.environ['AZURE_AI_SEARCH_INDEX_NAME'] = 'product-info-index-test1'
    os.environ['AZURE_OPENAI_CHAT_MODEL'] = 'gpt-35-turbo-16k'
    os.environ['AZURE_OPENAI_CHAT_DEPLOYMENT'] = 'gpt-35-turbo-16k-0613'
    os.environ['AZURE_OPENAI_EVALUATION_MODEL'] = 'gpt-35-turbo-16k'
    os.environ['AZURE_OPENAI_EVALUATION_DEPLOYMENT'] = 'gpt-35-turbo-16k-0613'
    os.environ['AZURE_OPENAI_EMBEDDING_MODEL'] = 'text-embedding-ada-002'
    os.environ['AZURE_OPENAI_EMBEDDING_DEPLOYMENT'] = 'text-ada-embedding-002-2'
    
class ChatCompletionLoader:
    def __init__(self, path):
        self.path = path
        self._initialize_environment_variables()
        self.chat_completion = chat_completion

    def _initialize_environment_variables(self):
        credential = ManagedIdentityCredential(client_id=os.getenv("UAI_CLIENT_ID"))
        client = AIClient(
            credential=credential,
            subscription_id=os.getenv("AZURE_SUBSCRIPTION_ID"),
            resource_group_name=os.getenv("AZURE_RESOURCE_GROUP_NAME"),
            project_name=os.getenv("AZURE_PROJECT_NAME"),
        )
        client.get_default_aoai_connection().set_current_environment()
        client.connections.get("Default_CognitiveSearch").set_current_environment()
        set_environment_variables()

    def predict(self, model_inputs):
        results = []
        for model_input in model_inputs:
            result = asyncio.run(
                output = self.chat_completion(model_input)
            )
            results.append(result)
        return results

def _load_pyfunc(path):
    return ChatCompletionLoader(path)


import os
import asyncio

from azure.ai.generative import AIClient
from azure.identity import DefaultAzureCredential

from azure.ai.generative.entities.deployment import Deployment
from azure.ai.generative.entities.models import LocalModel

from azure.identity import ManagedIdentityCredential
from azure.ai.generative import AIClient

from copilot_aisdk.chat import chat_completion
import run

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
        client.set_environment_variables()

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

def deploy_flow(deployment_name):
    client = AIClient.from_config(DefaultAzureCredential())
    deployment = Deployment(
        name=deployment_name,
        model=LocalModel(
            path="./src",
            conda_file="conda.yaml",
            loader_module="deploy",
        ),
    )    
    client.deployments.create_or_update(deployment)

if __name__ == "__main__":
    client = AIClient.from_config(DefaultAzureCredential())
    deploy_flow(f"{client.project_name}-copilot")
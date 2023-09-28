import os
from pathlib import Path
from azure.identity import ManagedIdentityCredential
from azure.ai.generative import AIClient
from langchain_model import LangchainModel

class ModelLoader:
    def __init__(self, path):
        self.path = path
        self._initialize_environment_variables()
        self.langchain_model = LangchainModel(path)

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

    def predict(self, model_inputs):
        results = []
        for model_input in model_inputs:
            output = self.langchain_model.qna(model_input)
            results.append(output)
        return results


def _load_pyfunc(path):
    return ModelLoader(path)
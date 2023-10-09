import os

from azure.ai.generative import AIClient
from azure.ai.generative.entities import Model, Deployment
from azure.identity import DefaultAzureCredential

client = AIClient.from_config(DefaultAzureCredential())
client.set_environment_variables()
    
flow = ChatCompletionFlow(
    path="./ai_sdk_copilot",
    conda_file="requirements.txt", # relative to model path if given
    loader_module="copilot.chat_completion" 
)

# Use secrets injection for keys so that we're not storing them in plain text anywhere
deployment_environment_variables = {
    "OPENAI_API_KEY": "azureml://connections/Default_AzureOpenAI/credentials/OPENAI_API_KEY",
    "OPENAI_API_BASE": "azureml://connections/connections/Default_AzureOpenAI/target",
    "OPENAI_API_VERSION": "azureml://connections/Default_AzureOpenAI/metadata/OPEN_AI_API_VERSION",
    "AZURE_SEARCH_TARGET": os.environ["AZURE_SEARCH_TARGET"],
    "AZURE_SEARCH_KEY": "azureml://connections/azure_cognitive_search_connection/credentials/COGNITIVE_SEARCH_KEY",
    "AZURE_SEARCH_INDEX_NAME": os.environ["AZURE_SEARCH_INDEX_NAME"],
    "AZURE_OPENAI_CHAT_DEPLOYMENT": os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT"],
    "AZURE_OPENAI_EVALUATION_DEPLOYMENT": os.environ["AZURE_OPENAI_EVALUATION_DEPLOYMENT"],
    "AZURE_OPENAI_EMBEDDING_MODEL": os.environ["AZURE_OPENAI_EMBEDDING_MODEL"],
    "AZURE_OPENAI_EMBEDDING_DEPLOYMENT": os.environ["AZURE_OPENAI_EMBEDDING_DEPLOYMENT"]
}

deployment = Deployment(
    name="my_custom_deployment",
    flow=flow,
    deployment_environment_variables,
    enable_data_collector=True,
    instance_type="Standard_DS3_v2",
)

client.deployments.create_or_update(deployment)
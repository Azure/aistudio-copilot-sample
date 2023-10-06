from azure.ai.generative import AIClient
from azure.identity import DefaultAzureCredential
from chat import chat_completion
from utils import create_cp_user_content, create_cp_assistant_content

# connects to project defined in the config.json file at the root of the repo
# Log into the Azure CLI (run az login --use-device code) before running this step!
client = AIClient.from_config(DefaultAzureCredential())

default_aoai_connection = client.get_default_aoai_connection()
default_aoai_connection.set_current_environment()
default_acs_connection = client.connections.get("Default_CognitiveSearch")
default_acs_connection.set_current_environment()

# Sample questions
questions = [
    "Which tent has the highest rainfly waterproof rating?",
    "What category is it belongs to?"
]
for question in questions:
    cp_messages = []
    print("* Question: " + question)
    cp_messages.append(create_cp_user_content(question))
    answer = chat_completion(cp_messages)
    print("* Answer: " + answer)
    cp_messages.append(create_cp_assistant_content(answer))

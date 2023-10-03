from promptflow import tool
from promptflow.connections import AzureOpenAIConnection, CognitiveSearchConnection
from chat import chat_completion
from utils import create_cp_user_content, \
  set_aoai_environment, \
  set_acs_environment

@tool
def chat_demo_tool(
  question: str,
  chat_history: list,
  aoai_connection: AzureOpenAIConnection,
  acs_connection: CognitiveSearchConnection
) -> str:
  cp_messages = []

  set_aoai_environment(aoai_connection)
  set_acs_environment(acs_connection)

  # Add the current question
  cp_messages.append(create_cp_user_content(question))

  result = chat_completion(cp_messages)
  return result

from __future__ import annotations

# set environment variables before importing any other code (in particular the openai module)
from dotenv import load_dotenv

load_dotenv()

import json
from pathlib import Path

# Import packages
import os
import sys
sys.path.insert(0, '../')
import asyncio
from typing import Callable, Dict, List

from azure.ai.resources.client import AIClient
from azure.ai.resources.entities import AzureOpenAIModelConfiguration
from azure.identity import DefaultAzureCredential
from azure.ai.generative.synthetic.simulator import Simulator, SimulatorTemplates
from azure.ai.generative.evaluate import evaluate
from copilot_aisdk.chat import chat_completion

def parse_args():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--task_type", default="conversation")
    parser.add_argument("--persona_file", default=None)
    parser.add_argument("--num_conv_turn", default=2)
    return parser.parse_args()

def get_ai_client():
    subscription_id: str = os.environ["AZURE_SUBSCRIPTION_ID"]
    resource_group_name: str = os.environ["AZURE_RESOURCE_GROUP"]
    project_name: str = os.environ["AZURE_AI_PROJECT_NAME"]
    config = {
        "subscription_id": subscription_id,
        "resource_group": resource_group_name,
        "project_name": project_name,
    }

    p = Path("config.json")

    with p.open(mode="w") as file:
        file.write(json.dumps(config))
    return AIClient.from_config(DefaultAzureCredential())

def get_bot_model(model_name = os.environ["AZURE_OPENAI_CHAT_MODEL"], 
                  deployment_name=os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT"], 
                  max_tokens=500, 
                  temperature=0.0):
    return AzureOpenAIModelConfiguration.from_connection(
        connection=default_aoai_connection,
        model_name= model_name,
        deployment_name=deployment_name,
        max_tokens=max_tokens,
        temperature=temperature
    )

def get_persona(file):
    with open(file, 'r') as f:
        content = f.read()
    return json.loads(content)


def create_callback_fn(callback_citation_key: str = "callback_citations", chat_completion_fn: Callable[[str, List[Dict], dict], str] = None):
    async def sim_callback(question, conversation_history, meta_data):
        # you may also await async call
        context_key = conv_template.context_key[0]
        messages = []
        for i in range(len(conversation_history)):
            turn = conversation_history[i]
            message = turn.to_openai_chat_format()
            messages.append(message)

        response = await chat_completion_fn(messages = messages)
        context_dict = {"turn_" + str(i + 1): response.choices[0]['context']}
        meta_data[context_key]["callback_citation_key"] = callback_citation_key
        if "context" in meta_data[context_key].keys():
            meta_data[context_key][callback_citation_key].update(context_dict)
        else:
            meta_data[context_key][callback_citation_key] = context_dict
        return response.choices[0]["message"]['content']
    return sim_callback

if __name__ == '__main__':
    args = parse_args()
    task_type = args.task_type
    persona_file = args.persona_file
    num_conv_turn = args.num_conv_turn

    ### validate parameters
    if task_type not in ["conversation"]:
        raise Exception("f{task_type} is not supported.")
    try:
        num_conv_turn = int(num_conv_turn)
    except:
        raise Exception("num_conv_turn must be an integer.")
    try:
        conv_parameters = get_persona(persona_file)
    except:
        raise Exception("fail to load f{persona_file}")

    ### connect to workspace
    ai_client = get_ai_client()
    # Get the default Azure Open AI connection for your project
    default_aoai_connection = ai_client.get_default_aoai_connection()
    system_bot_model = get_bot_model()

    st = SimulatorTemplates()

    # retrieve template for conversation task
    conv_template = st.get_template(task_type)

    # retrieve parameters in the template
    conv_parameters = st.get_template_parameters(task_type)

    # initialize the conversation template parameters
    conv_parameters = get_persona(persona_file)

    sim_callback = create_callback_fn("callback_citations", chat_completion)

    simulator = Simulator(simulate_callback=sim_callback, systemConnection=system_bot_model)
    conv_callback = asyncio.run(simulator.simulate_async(
                                conv_template,
                                conv_parameters,
                                max_conversation_turns=num_conv_turn,
                                api_call_delay_sec=10,
                                api_call_retry_sleep_sec=10,
                                api_call_retry_max_count=2,
                            ))

    ### evaluate simulated chat
    data_input_file = 'simulator_conv.jsonl'
    with open(data_input_file, 'w', encoding='utf-8') as file:
        json.dump(conv_callback, file)

    data_mapping = {"y_pred": "messages"}
    metrics = ['gpt_groundedness', 'gpt_relevance', 'gpt_retrieval_score']
    openai_params = {
                "api_version": os.getenv("OPENAI_API_VERSION"),
                "api_base": os.getenv("OPENAI_API_BASE"),
                "api_type": os.getenv("OPENAI_API_TYPE"),
                "api_key": os.getenv("OPENAI_API_KEY"),
                "deployment_id": os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT"]
        }

    result = evaluate(
        evaluation_name="simulator-with-sdk_chatcompletion-baseline-evaluation",
        data=data_input_file,
        task_type="chat",
        model_config=openai_params,
        data_mapping = data_mapping,
        metrics_list = metrics,
        tracking_uri=ai_client.tracking_uri,
    )
    print(result.metrics_summary)
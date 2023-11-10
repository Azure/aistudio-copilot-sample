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

from azure.ai.resources.client import AIClient
from azure.ai.resources.entities import AzureOpenAIModelConfiguration
from azure.identity import DefaultAzureCredential
from azure.ai.generative.synthetic.simulator import Simulator, SimulatorTemplates
from azure.ai.generative.evaluate import evaluate
from copilot_aisdk.chat import chat_completion

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


async def sim_callback(question, conversation_history, meta_data):
    # you may also await async call
    context_key = conv_template.context_key[0]
    messages = []
    for i in range(len(conversation_history)):
        turn = conversation_history[i]
        message = turn.to_openai_chat_format()
        messages.append(message)
        
    response = await chat_completion(messages = messages)
    context_dict = {"turn_" + str(i + 1): response.choices[0]['context']}
    if "context" in meta_data[context_key].keys():
        meta_data[context_key]["context"].update(context_dict)
    else:
        meta_data[context_key]["context"] = context_dict
    return response.choices[0]["message"]['content']

if __name__ == '__main__':
    ai_client = get_ai_client()
    # Get the default Azure Open AI connection for your project
    default_aoai_connection = ai_client.get_default_aoai_connection()
    system_bot_model = get_bot_model()

    st = SimulatorTemplates()

    # retrieve template for conversation task
    task_type = "conversation"
    conv_template = st.get_template(task_type)

    # retrieve parameters in the template
    conv_parameters = st.get_template_parameters(task_type)

    # initialize the conversation template parameters
    conv_parameters = {
        "name": "Jane",
        "profile": """
        Jane Doe is a 28-year-old outdoor enthusiast 
        who lives in Seattle, Washington. 
        She has a passion for exploring nature and loves going on camping and hiking trips with her friends. 
        She has recently become a member of the company's loyalty program and has achieved Bronze level status."""
        """Jane has a busy schedule, but she always makes time for her outdoor adventures.
        She is constantly looking for high-quality gear that can help her make the most of her trips and ensure she has a comfortable experience in the outdoors."""
        """Recently, Jane purchased a TrailMaster X4 Tent from the company. 
        This tent is perfect for her needs, as it is both durable and spacious, allowing her to enjoy her camping trips with ease. 
        The price of the tent was $250, and it has already proved to be a great investment."""
        "In addition to the tent, Jane also bought a Pathfinder Pro-1 Adventure Compass for $39.99. This compass has helped her navigate challenging trails with confidence, ensuring that she never loses her way during her adventures."
        "Finally, Jane decided to upgrade her sleeping gear by purchasing a CozyNights Sleeping Bag for $100. This sleeping bag has made her camping nights even more enjoyable, as it provides her with the warmth and comfort she needs after a long day of hiking.",
        "tone": "happy",
        "metadata": {
            "customer_info": "## customer_info      name: Jane Doe    age: 28     phone_number: 555-987-6543     email: jane.doe@example.com     address: 789 Broadway St, Seattle, WA 98101      loyalty_program: True     loyalty_program Level: Bronze        ## recent_purchases      order_number: 5  date: 2023-05-01  item: - description:  TrailMaster X4 Tent, quantity 1, price $250    item_number: 1   order_number: 18  date: 2023-05-04  item: - description:  Pathfinder Pro-1 Adventure Compass, quantity 1, price $39.99    item_number: 4   order_number: 28  date: 2023-04-15  item: - description:  CozyNights Sleeping Bag, quantity 1, price $100    item_number: 7"
        },
        "task": "Jane is trying to accomplish the task of finding out the best hiking backpacks suitable for her weekend camping trips, and how they compare with other options available in the market. She wants to make an informed decision before making a purchase from the outdoor gear company's website or visiting their physical store."
        "Jane uses Google to search for 'best hiking backpacks for weekend trips,' hoping to find reliable and updated information from official sources or trusted websites. She expects to see a list of top-rated backpacks, their features, capacity, comfort, durability, and prices. She is also interested in customer reviews to understand the pros and cons of each backpack."
        "Furthermore, Jane wants to see the specifications, materials used, waterproof capabilities, and available colors for each backpack. She also wants to compare the chosen backpacks with other popular brands like Osprey, Deuter, or Gregory. Jane plans to spend about 20 minutes on this task and shortlist two or three options that suit her requirements and budget."
        "Finally, as a Bronze level member of the outdoor gear company's loyalty program, Jane might also want to contact customer service to inquire about any special deals or discounts available on her shortlisted backpacks, ensuring she gets the best value for her purchase.",
        "chatbot_name": "ChatBot",
    }

    simulator = Simulator(simulate_callback=sim_callback, systemConnection=system_bot_model)
    conv_callback = asyncio.run(simulator.simulate_async(
                                conv_template,
                                conv_parameters,
                                max_conversation_turns=4,
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
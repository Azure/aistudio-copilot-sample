# enable type annotation syntax on Python versions earlier than 3.9
from __future__ import annotations
import datetime

import os
import pathlib
from typing import Any
import jinja2
import openai

import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.planning import StepwisePlanner
from semantic_kernel.planning.stepwise_planner.stepwise_planner_config import StepwisePlannerConfig
from copilot_semantickernel.plugins.customer_support_plugin.customer_support import CustomerSupport
from streaming_utils import add_context_to_streamed_response

templateLoader = jinja2.FileSystemLoader(pathlib.Path(__file__).parent.resolve())
templateEnv = jinja2.Environment(loader=templateLoader)
system_message_template = templateEnv.get_template("system-message.jinja2")

async def chat_completion(messages: list[dict], stream: bool = False, 
    session_state: Any = None, context: dict[str, Any] = {}):

    # Get the message from the user
    user_message = messages[-1]["content"]

    # Initialize the kernel
    kernel = sk.Kernel()
    kernel.add_chat_service(
        "chat_completion",
        AzureChatCompletion(
            os.environ.get("AZURE_OPENAI_CHAT_DEPLOYMENT"),
            os.getenv("OPENAI_API_BASE"),
            os.getenv("OPENAI_API_KEY"),
        )
    )

    customer_support_plugin = CustomerSupport(
        number_of_docs = context.get("num_retrieved_docs", 10),
        embedding_model_deployment = os.environ["AZURE_OPENAI_EMBEDDING_MODEL"],
        chat_model_deployment=os.environ.get("AZURE_OPENAI_CHAT_DEPLOYMENT"),
        temperature=context.get("temperature", 0.7)
    )
    
    # Add the customer support plugin to the kernel
    kernel.import_skill(customer_support_plugin, skill_name="CustomerSupport")

    # Add hints to the customer ask
    # TODO: Make the ID configurable
    ask = user_message + "\nThe customer ID is 1; only use this if you need information about the current customer."

    # Create and run plan based on the customer ask
    planner = StepwisePlanner(kernel, config=StepwisePlannerConfig(max_iterations=5))
    plan = planner.create_plan(ask)
    result = await kernel.run_async(plan)

    # limit size of returned context
    planner_context = customer_support_plugin.context
    if len(context) > 40000:
        planner_context = context[:40000]


    # add retrieved documents as context to the system prompt
    system_message = system_message_template.render(answer=result["input"])
    messages.insert(0, {"role": "system", "content": system_message})

    # call Azure OpenAI with the system prompt and user's question
    response = openai.ChatCompletion.create(
        engine=os.environ.get("AZURE_OPENAI_CHAT_DEPLOYMENT"),
        messages=messages, temperature=context.get("temperature", 0.7),
        stream=stream,
        max_tokens=800)

    # add context in the returned response
    if not stream:
        response.choices[0]['context'] = planner_context
    else:
        response = add_context_to_streamed_response(response, planner_context)
    return response


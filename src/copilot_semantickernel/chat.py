# enable type annotation syntax on Python versions earlier than 3.9
from __future__ import annotations
import datetime

import os
from typing import Any

import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.planning import StepwisePlanner
from semantic_kernel.planning.stepwise_planner.stepwise_planner_config import StepwisePlannerConfig
from copilot_semantickernel.plugins.customer_support_plugin.customer_support import CustomerSupport


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
    
    # Add the customer support plugin to the kernel
    kernel.import_skill(CustomerSupport(
        number_of_docs = context.get("num_retrieved_docs", 5),
        embedding_model_deployment = os.environ["AZURE_OPENAI_EMBEDDING_MODEL"],
        chat_model_deployment=os.environ.get("AZURE_OPENAI_CHAT_DEPLOYMENT"),
        temperature=context.get("temperature", 0.7)
    ), skill_name="CustomerSupport")

    # Create and run plan based on the customer ask
    planner = StepwisePlanner(kernel, config=StepwisePlannerConfig(max_iterations=5))
    plan = planner.create_plan(user_message)
    result = await kernel.run_async(plan)

    # Print the steps taken by the stepwise planner for debugging purposes
    print(result.variables["steps_taken"])

    return {
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": result.result
            },
            "extra_args": {
                "context": result.variables["skill_count"]
            }
        }]
    }


# enable type annotation syntax on Python versions earlier than 3.9
from __future__ import annotations

# set environment variables before importing any other code (in particular the openai module)
from dotenv import load_dotenv
load_dotenv()

import os
import sys
import asyncio
import platform
import json
import pathlib

from azure.ai.resources.client import AIClient
from azure.ai.resources.entities.models import Model
from azure.ai.resources.entities.deployment import Deployment
from azure.identity import DefaultAzureCredential
from consts import search_index_name, search_index_folder

# build the index using the product catalog docs from data/3-product-info
def build_cogsearch_index(index_name, path_to_data):
    from azure.ai.resources.operations._index_data_source import LocalSource, ACSOutputConfig
    from azure.ai.generative.index import build_index

    # Set up environment variables for cog search SDK
    os.environ["AZURE_COGNITIVE_SEARCH_TARGET"] = os.environ["AZURE_AI_SEARCH_ENDPOINT"]
    os.environ["AZURE_COGNITIVE_SEARCH_KEY"] = os.environ["AZURE_AI_SEARCH_KEY"]

    client = AIClient.from_config(DefaultAzureCredential())

    # Use the same index name when registering the index in AI Studio
    index = build_index(
        output_index_name=index_name,
        vector_store="azure_cognitive_search",
        embeddings_model = f"azure_open_ai://deployment/{os.environ['AZURE_OPENAI_EMBEDDING_DEPLOYMENT']}/model/{os.environ['AZURE_OPENAI_EMBEDDING_MODEL']}",
        data_source_url="https://product_info.com",
        index_input_config=LocalSource(input_data=path_to_data),
        acs_config=ACSOutputConfig(
            acs_index_name=index_name,
        ),
    )

    # register the index so that it shows up in the project
    cloud_index = client.indexes.create_or_update(index)

    print(f"Created index '{cloud_index.name}'")
    print(f"Local Path: {index.path}")
    print(f"Cloud Path: {cloud_index.path}")

# TEMP: wrapper around chat completion function until chat_completion protocol is supported
def copilot_qna(question, chat_completion_fn):
    # Call the async chat function with a single question and print the response

    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    result = asyncio.run(
        chat_completion_fn([{"role": "user", "content": question}])
    )
    response = result['choices'][0]
    return {
        "question": question,
        "answer": response["message"]["content"],
        "context": response["context"]
    }

 # Define helper methods
def load_jsonl(path):
    with open(path, "r") as f:
        return [json.loads(line) for line in f.readlines()]

def run_evaluation(chat_completion_fn, name, dataset_path):
    from azure.ai.generative.evaluate import evaluate

    # Evaluate the default vs the improved system prompt to see if the improved prompt
    # performs consistently better across a larger set of inputs
    path = pathlib.Path.cwd() / dataset_path
    dataset = load_jsonl(path)

    # temp: generate a single-turn qna wrapper over the chat completion function
    qna_fn = lambda question: copilot_qna(question, chat_completion_fn)


    client = AIClient.from_config(DefaultAzureCredential())
    result = evaluate(
        evaluation_name=name,
        target=qna_fn,
        data=dataset,
        task_type="qa",
        data_mapping={
            "questions": "question",
            "contexts": "context",
            "y_pred": "answer",
            "y_test": "truth"
        },
        model_config={
            "api_version": "2023-05-15",
            "api_base": os.getenv("OPENAI_API_BASE"),
            "api_type": "azure",
            "api_key": os.getenv("OPENAI_API_KEY"),
            "deployment_id": os.getenv("AZURE_OPENAI_EVALUATION_DEPLOYMENT")
        },
        tracking_uri=client.tracking_uri,
    )
    return result.metrics_summary

def deploy_flow(deployment_name, deployment_folder, chat_module):
    client = AIClient.from_config(DefaultAzureCredential())
    deployment = Deployment(
        name=deployment_name,
        model=Model(
            path=".",
            conda_file=f"{deployment_folder}/conda.yaml",
            chat_module=chat_module,
        ),
        instance_type="Standard_DS2_V2",
        environment_variables={
            'OPENAI_API_TYPE': "${{azureml://connections/Default_AzureOpenAI/metadata/ApiType}}" ,
            'OPENAI_API_BASE': "${{azureml://connections/Default_AzureOpenAI/target}}",
            'OPENAI_API_KEY': "${{azureml://connections/Default_AzureOpenAI/credentials/key}}",
            'OPENAI_API_VERSION': "${{azureml://connections/Default_AzureOpenAI/metadata/ApiVersion}}",
            'AZURE_AI_SEARCH_ENDPOINT': "${{azureml://connections/Default_CognitiveSearch/target}}",
            'AZURE_AI_SEARCH_KEY': "${{azureml://connections/Default_CognitiveSearch/credentials/key}}",
            'AZURE_AI_SEARCH_INDEX_NAME': os.getenv('AZURE_AI_SEARCH_INDEX_NAME'),
            'AZURE_OPENAI_CHAT_MODEL': os.getenv('AZURE_OPENAI_CHAT_MODEL'),
            'AZURE_OPENAI_CHAT_DEPLOYMENT': os.getenv('AZURE_OPENAI_CHAT_DEPLOYMENT'),
            'AZURE_OPENAI_EVALUATION_MODEL': os.getenv('AZURE_OPENAI_EVALUATION_MODEL'),
            'AZURE_OPENAI_EVALUATION_DEPLOYMENT': os.getenv('AZURE_OPENAI_EVALUATION_DEPLOYMENT'),
            'AZURE_OPENAI_EMBEDDING_MODEL': os.getenv('AZURE_OPENAI_EMBEDDING_MODEL'),
            'AZURE_OPENAI_EMBEDDING_DEPLOYMENT': os.getenv('AZURE_OPENAI_EMBEDDING_DEPLOYMENT'),
        },
    )
    client.deployments.create_or_update(deployment)

# Run a single chat message through one of the co-pilot implementations
if __name__ == "__main__":
    # configure asyncio
    import asyncio
    import platform

    # workaround for a bug on windows
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--question", help="The question to ask the copilot", type=str)
    parser.add_argument("--implementation", help="The implementation to use", default="aisdk", type=str)
    parser.add_argument("--deploy", help="Deploy copilot", action='store_true')
    parser.add_argument("--evaluate", help="Evaluate copilot", action='store_true')
    parser.add_argument("--dataset-path", help="Test dataset to use with evaluation", default="src/tests/evaluation_dataset.jsonl", action='store_true')
    parser.add_argument("--deployment-name", help="deployment name to use when deploying the flow", type=str)
    parser.add_argument("--build-index", help="Build an index with the default docs", action='store_true')
    args = parser.parse_args()

    if args.implementation:
        if args.implementation == "promptflow":
            from copilot_promptflow.chat import chat_completion
            deployment_folder = "copilot_promptflow"
            chat_module = "copilot_promptflow.chat"
        elif args.implementation == "semantickernel":
            from copilot_semantickernel.chat import chat_completion
            deployment_folder = "copilot_semantickernel"
            chat_module = "copilot_semantickernel.chat"
        elif args.implementation == "langchain":
            from copilot_langchain.chat import chat_completion
            deployment_folder = "copilot_langchain"
            chat_module = "copilot_langchain.chat"
        elif args.implementation == "aisdk":
            from copilot_aisdk.chat import chat_completion
            deployment_folder = "copilot_aisdk"
            chat_module = "copilot_aisdk.chat"

    if args.build_index:
        build_cogsearch_index(os.getenv("AZURE_AI_SEARCH_INDEX_NAME"), "./data/3-product-info")
    elif args.evaluate:
        results = run_evaluation(chat_completion, name=f"test-{args.implementation}-copilot", dataset_path=args.dataset_path)
        print(results)
    elif args.deploy:
        client = AIClient.from_config(DefaultAzureCredential())
        deployment_name = args.deployment_name if args.deployment_name else f"{client.project_name}-copilot"
        deploy_flow(deployment_name, deployment_folder, chat_module)
    else:
        question = "which tent is the most waterproof?"
        if args.question:
            question = args.question

        # Prepare for the search index
        if not os.path.exists(search_index_folder):
            client = AIClient.from_config(DefaultAzureCredential())
            try:
                client.mlindexes.download(name=search_index_name, download_path=search_index_folder, label="latest")
            except:
                print("Please build the search index with 'python src/run.py --build-index'")
                sys.exit(1)

        # Call the async chat function with a single question and print the response
        result = asyncio.run(
            chat_completion([{"role": "user", "content": question}])
        )
        print(result)

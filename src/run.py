# enable type annotation syntax on Python versions earlier than 3.9
from __future__ import annotations

import tempfile
from pprint import pprint

# set environment variables before importing any other code (in particular the openai module)
from dotenv import load_dotenv

load_dotenv()

import os
import sys
import asyncio
import platform
import json
import pathlib
import pandas as pd

from functools import partial

from azure.ai.resources.client import AIClient
from azure.ai.resources.entities.models import Model
from azure.ai.resources.entities.single_deployment import SingleDeployment
from azure.identity import DefaultAzureCredential

from openai.types.chat import ChatCompletion

source_path = "./src"

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
        embeddings_model=f"azure_open_ai://deployment/{os.environ['AZURE_OPENAI_EMBEDDING_DEPLOYMENT']}/model/{os.environ['AZURE_OPENAI_EMBEDDING_MODEL']}",
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
def copilot_qna(*, question, chat_completion_fn, **kwargs):
    # Call the async chat function with a single question and print the response

    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    result = asyncio.run(
        chat_completion_fn([{"role": "user", "content": question}])
    )

    return {
        "question": question,
        "answer": result.choices[0].message.content if isinstance(result, ChatCompletion) else result["choices"][0]["message"]["content"],
        "context": result.choices[0].context if isinstance(result, ChatCompletion) else result["choices"][0]["context"]
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
    qna_fn = partial(copilot_qna, chat_completion_fn=chat_completion_fn)
    output_path = "./evaluation_output"

    client = AIClient.from_config(DefaultAzureCredential())
    result = evaluate(
        evaluation_name=name,
        target=qna_fn,
        data=dataset,
        task_type="qa",
        data_mapping={ 
            # Your data or output of target function need to contain "question", "answer", "context" and "grounth_truth" columns. Use data_mapping to match.
            "ground_truth": "truth"
        },
        model_config={
            "api_version": "2023-05-15",
            "api_base": os.getenv("OPENAI_API_BASE"),
            "api_type": "azure",
            "api_key": os.getenv("OPENAI_API_KEY"),
            "deployment_id": os.getenv("AZURE_OPENAI_EVALUATION_DEPLOYMENT")
        },
        metrics_list=["exact_match", "gpt_groundedness", "gpt_relevance", "gpt_coherence"],
        tracking_uri=client.tracking_uri,
        output_path=output_path,
    )
    
    tabular_result = pd.read_json(os.path.join(output_path, "eval_results.jsonl"), lines=True)

    return result, tabular_result

def prepare_search_index(deployment_folder: str):
    client = AIClient.from_config(DefaultAzureCredential())
    search_index_name = os.getenv("AZURE_AI_SEARCH_INDEX_NAME")
    search_index_folder = (search_index_name if search_index_name else "") + "-mlindex"
    search_index_path = os.path.join(source_path, deployment_folder, search_index_folder)
    if not os.path.exists(search_index_path):
        try:
            client.indexes.download(name=os.getenv("AZURE_AI_SEARCH_INDEX_NAME"),
                                        download_path=search_index_path, label="latest")
        except:
            print("Please build the search index with 'python src/run.py --build-index'")
            sys.exit(1)

def deploy_flow(deployment_name, deployment_folder, chat_module):
    client = AIClient.from_config(DefaultAzureCredential())

    if not deployment_name:
        deployment_name = f"{client.project_name}-copilot"
    deployment = SingleDeployment(
        name=deployment_name,
        model=Model(
            path=source_path,
            conda_file=f"{deployment_folder}/conda.yaml",
            chat_module=chat_module,
        ),
        environment_variables={
            'OPENAI_API_TYPE': "${{azureml://connections/Default_AzureOpenAI/metadata/ApiType}}",
            'OPENAI_API_BASE': "${{azureml://connections/Default_AzureOpenAI/target}}",
            'AZURE_OPENAI_ENDPOINT': "${{azureml://connections/Default_AzureOpenAI/target}}",
            'OPENAI_API_KEY': "${{azureml://connections/Default_AzureOpenAI/credentials/key}}",
            'AZURE_OPENAI_KEY': "${{azureml://connections/Default_AzureOpenAI/credentials/key}}",
            'OPENAI_API_VERSION': "${{azureml://connections/Default_AzureOpenAI/metadata/ApiVersion}}",
            'AZURE_OPENAI_API_VERSION': "${{azureml://connections/Default_AzureOpenAI/metadata/ApiVersion}}",
            'AZURE_AI_SEARCH_ENDPOINT': "${{azureml://connections/AzureAISearch/target}}",
            'AZURE_AI_SEARCH_KEY': "${{azureml://connections/AzureAISearch/credentials/key}}",
            'AZURE_AI_SEARCH_INDEX_NAME': os.getenv('AZURE_AI_SEARCH_INDEX_NAME'),
            'AZURE_OPENAI_CHAT_MODEL': os.getenv('AZURE_OPENAI_CHAT_MODEL'),
            'AZURE_OPENAI_CHAT_DEPLOYMENT': os.getenv('AZURE_OPENAI_CHAT_DEPLOYMENT'),
            'AZURE_OPENAI_EVALUATION_MODEL': os.getenv('AZURE_OPENAI_EVALUATION_MODEL'),
            'AZURE_OPENAI_EVALUATION_DEPLOYMENT': os.getenv('AZURE_OPENAI_EVALUATION_DEPLOYMENT'),
            'AZURE_OPENAI_EMBEDDING_MODEL': os.getenv('AZURE_OPENAI_EMBEDDING_MODEL'),
            'AZURE_OPENAI_EMBEDDING_DEPLOYMENT': os.getenv('AZURE_OPENAI_EMBEDDING_DEPLOYMENT'),
        },
        instance_count=1
    )
    client._single_deployments.begin_create_or_update(deployment)


def invoke_deployment(deployment_name: str, stream: bool = False):
    client = AIClient.from_config(DefaultAzureCredential())
    if not deployment_name:
        deployment_name = f"{client.project_name}-copilot"
    import requests

    if stream:
        accept_header = "application/jsonl"
    else:
        accept_header = "application/json"

    scoring_url = client._single_deployments.get(deployment_name).scoring_uri
    primary_key = client._single_deployments.get_keys(deployment_name).primary_key

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {primary_key}",
        "Accept": accept_header,
        "azureml-model-deployment": deployment_name,
    }

    response = requests.post(
        scoring_url,
        headers=headers,
        json={
            "messages": [{"role": "user", "content": "What tent has the highest rainfly rating?"}],
            "stream": stream,
        },
        stream=stream
    )
    if stream:
        for item in response.iter_lines(chunk_size=None):
            print(item)
    else:
        print(response.json())



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
    parser.add_argument("--evaluation-name", help="evaluation name used to log the evaluation to AI Studio", type=str)
    parser.add_argument("--dataset-path", help="Test dataset to use with evaluation",
                        default="src/tests/evaluation_dataset.jsonl", action='store_true')
    parser.add_argument("--deployment-name", help="deployment name to use when deploying or invoking the flow", type=str)
    parser.add_argument("--build-index", help="Build an index with the default docs", action='store_true')
    parser.add_argument("--stream", help="Whether response from a particular implementation should be streamed or not", action="store_true")
    parser.add_argument("--invoke-deployment", help="Invoke a deployment and print out response", action="store_true")
    args = parser.parse_args()

    if args.implementation:
        if args.implementation == "promptflow":
            from copilot_promptflow.chat import chat_completion

            deployment_folder = "copilot_promptflow"
            chat_module = "copilot_promptflow.chat"
        elif args.implementation == "langchain":
            from copilot_langchain.chat import chat_completion

            deployment_folder = "copilot_langchain"
            chat_module = "copilot_langchain.chat"

            # Only LangChain uses local search index currently
            prepare_search_index(deployment_folder)
        elif args.implementation == "aisdk":
            from copilot_aisdk.chat import chat_completion

            deployment_folder = "copilot_aisdk"
            chat_module = "copilot_aisdk.chat"

    if args.build_index:
        build_cogsearch_index(os.getenv("AZURE_AI_SEARCH_INDEX_NAME"), "./data/3-product-info")
    elif args.evaluate:
        evaluation_name = args.evaluation_name if args.evaluation_name else f"test-{args.implementation}-copilot"
        result, tabular_result = run_evaluation(chat_completion, name=evaluation_name,
                                 dataset_path=args.dataset_path)
        pprint("-----Summarized Metrics-----")
        pprint(result.metrics_summary)
        pprint("-----Tabular Result-----")
        pprint(tabular_result)
        pprint(f"View evaluation results in AI Studio: {result.studio_url}")
    elif args.deploy:
        deployment_name = args.deployment_name if args.deployment_name else None
        deploy_flow(deployment_name, deployment_folder, chat_module)
    elif args.invoke_deployment:
        invoke_deployment(args.deployment_name, stream=args.stream)
    else:
        question = "which tent is the most waterproof?"
        if args.question:
            question = args.question

        # Call the async chat function with a single question and print the response
        if args.stream:
            result = asyncio.run(
                chat_completion([{"role": "user", "content": question}], stream=True)
            )
            for r in result:
                print(r)
                print("\n")
        else:
            result = asyncio.run(
                chat_completion([{"role": "user", "content": question}], stream=False)
            )
            print(result)

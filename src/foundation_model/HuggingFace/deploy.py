# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from argparse import ArgumentParser

from azure.ai.resources import AIClient
from azure.ai.resources.entities.deployment import Deployment
from azure.identity import DefaultAzureCredential as Credential

def deploy(deployment_name: str):
    credential = Credential()

    model_id = "azureml://registries/HuggingFace/models/t5-small/versions/19"

    client = AIClient.from_config(credential)

    deployment = Deployment(
        name=deployment_name,
        model=model_id,
    )

    deployment = client.deployments.create_or_update(deployment)

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--deployment-name", help="Name of the deployment. Deployment name must be unique within a given region")
    parsed_args = parser.parse_args()
    deploy(parsed_args.deployment_name)
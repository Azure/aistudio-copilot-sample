# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from argparse import ArgumentParser

from azure.ai.resources.client import AIClient
from azure.ai.resources.entities.deployment import Deployment
from azure.identity import DefaultAzureCredential as Credential

def invoke(deployment_name: str):
    credential = Credential()

    client = AIClient.from_config(credential)

    client.deployments.invoke(deployment_name, "./request_file.json")

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--deployment-name", help="Name of the deployment to invoke")
    parsed_args = parser.parse_args()
    invoke(parsed_args.deployment_name)

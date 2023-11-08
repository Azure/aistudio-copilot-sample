# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from argparse import ArgumentParser

from azure.ai.resources.client import AIClient
from azure.ai.resources.entities.deployment import Deployment
from azure.identity import InteractiveBrowserCredential as Credential

def invoke(deployment_name: str):
    credential = Credential()

    client = AIClient.from_config(credential)

    return client.deployments.invoke(deployment_name, "./request_file.json")

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--deployment-name", help="Name of the deployment to invoke")
    parsed_args = parser.parse_args()
    result = invoke(parsed_args.deployment_name)
    print(result)
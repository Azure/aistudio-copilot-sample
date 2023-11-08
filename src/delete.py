# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from argparse import ArgumentParser

from azure.ai.resources.client import AIClient
from azure.identity import InteractiveBrowserCredential as Credential


def delete(deployment_name: str):
    credential = Credential()

    client = AIClient.from_config(credential)

    client.deployments.delete(deployment_name)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--deployment-name", help="Name of the deployment. Deployment name must be unique within a given region")
    parsed_args = parser.parse_args()

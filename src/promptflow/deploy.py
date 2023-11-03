# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from argparse import ArgumentParser

from azure.ai.resources.client import AIClient
from azure.ai.resources.entities.deployment import Deployment
from azure.ai.resources.entities.models import PromptflowModel
from azure.identity import InteractiveBrowserCredential as Credential


def deploy(deployment_name: str):
    credential = Credential()

    client = AIClient.from_config(credential)

    deployment = Deployment(
        name=deployment_name,
        model=PromptflowModel(
            path="./flow-with-connections/"
        ),
    )

    deployment = client.deployments.create_or_update(deployment)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--deployment-name", help="Name of the deployment. Deployment name must be unique within a given region")
    parsed_args = parser.parse_args()
    deploy(parsed_args.deployment_name)
# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import json

from argparse import ArgumentParser

from azure.ai.resources.client import AIClient
from azure.ai.resources.entities import Project
from azure.identity import InteractiveBrowserCredential as Credential


def deploy(project_name: str):
    credential = Credential()

    subscription_id = "b17253fa-f327-42d6-9686-f3e553e24763"
    resource_group_name = "rg-deploymentbugbash"

    project = Project(
        name=project_name,
        ai_resource="/subscriptions/b17253fa-f327-42d6-9686-f3e553e24763/resourceGroups/rg-deploymentbugbash/providers/Microsoft.MachineLearningServices/workspaces/deployment_bug_bash"
    )

    client = AIClient(
        credential=credential,
        subscription_id=subscription_id,
        resource_group_name=resource_group_name,
    )

    print(f"creating project with name {project_name} using AI resource deployment_bug_bash")
    client.projects.begin_create(project=project).wait()
    print("done")

    with open("config.json", "w+") as f:
        json.dump(
            {
                "subscription_id": subscription_id,
                "resource_group_name": resource_group_name,
                "project_name": project_name
            },
            f,
            indent=4,
        )


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--project-name", help="Name of the project", required=True)
    parsed_args = parser.parse_args()
    deploy(parsed_args.project_name)
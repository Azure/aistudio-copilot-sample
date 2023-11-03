# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import requests
import json
from argparse import ArgumentParser

from azure.ai.resources import AIClient
from azure.identity import DefaultAzureCredential as Credential

def invoke(deployment_name: str):
    credential = Credential()

    client = AIClient.from_config(credential)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {client.deployments.get_keys(deployment_name).primary_key}",
        "Accept": "text/event-stream",
    }


    with open("./request_file.json", "r") as f:
        json_body = json.load(f)

    response = requests.post(
        client.deployments.get(deployment_name).scoring_uri,
        headers=headers,
        json=json_body,
        stream=True
    )
    for item in response.iter_lines(chunk_size=None):
        print(item)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--deployment-name", help="Name of the deployment to invoke")
    parsed_args = parser.parse_args()
    invoke(parsed_args.deployment_name)
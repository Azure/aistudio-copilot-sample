import asyncio
import json
import os
from pathlib import Path
import sys
from azureml.contrib.services.aml_request import AMLRequest, rawhttp
from azureml.contrib.services.aml_response import AMLResponse
import json
import importlib


def response_to_dict(response):
    for resp in response:
        yield json.dumps(resp) + "\n"

def init():
    """
    This function is called when the container is initialized/started, typically after create/update of the deployment.
    You can write the logic here to perform init operations like caching the model in memory
    """
    # AZUREML_MODEL_DIR is an environment variable created during deployment.
    # It is the path to the model folder (./azureml-models/$MODEL_NAME/$VERSION)
    # Please provide your model's folder name if there is one
    resolved_path = str(Path(os.getenv("AZUREML_MODEL_DIR")).resolve())
    sys.path.append(resolved_path)

@rawhttp
def run(raw_data: AMLRequest):
    """
    This function is called for every invocation of the endpoint to perform the actual scoring/prediction.
    In the example we extract the data from the json input and call the scikit-learn model's predict()
    method and return the result back
    """
    raw_data = json.loads(raw_data.data)
    stream = raw_data["stream"]
    chat_completion = importlib.import_module(os.getenv("AZURE_AI_CHAT_MODULE")).chat_completion
    response = asyncio.run(chat_completion(**raw_data))
    if stream:
        aml_response = AMLResponse(response_to_dict(response), 200)
        aml_response.headers["Content-Type"] = "text/event-stream"
        return aml_response
    return json.dumps(response)

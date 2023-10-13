import json
import os
from pathlib import Path
import sys
from azureml.contrib.services.aml_request import AMLRequest, rawhttp 
from azureml.contrib.services.aml_response import AMLResponse 
import openai
import time, logging, json


def response_to_dict(response):
    for resp in response:
        yield response["choices"][0]["content"]
        yield json.dumps(resp.to_dict_recursive()) + "\n"


def generate(response):
    for resp in response:
        yield resp


def init():
    """
    This function is called when the container is initialized/started, typically after create/update of the deployment.
    You can write the logic here to perform init operations like caching the model in memory
    """
    # AZUREML_MODEL_DIR is an environment variable created during deployment.
    # It is the path to the model folder (./azureml-models/$MODEL_NAME/$VERSION)
    # Please provide your model's folder name if there is one
    resolved_path = str(Path(os.getenv("AZUREML_MODEL_DIR")).resolve() / "copilot_aisdk")
    sys.path.append(resolved_path)
    openai.api_key = os.getenv("AZUREML_MODEL_DIR")
    openai.api_base = "https://test-aoai-eus.openai.azure.com/"
    openai.api_type = 'azure'
    openai.api_version = '2023-05-15' # this may change in the future


@rawhttp
def run(raw_data: AMLRequest):
    """
    This function is called for every invocation of the endpoint to perform the actual scoring/prediction.
    In the example we extract the data from the json input and call the scikit-learn model's predict()
    method and return the result back
    """
    print(raw_data.headers)
    raw_data = json.loads(raw_data.data)
    message = raw_data["question"]
    stream = raw_data["stream"]
    # from call_openai import call_model
    # response = call_model(message, stream=stream)
    response = openai.ChatCompletion.create(
        engine='gpt-35-turbo',
        messages=[
            {'role': 'user', 'content': message}
        ],
        temperature=0,
        stream=True  # this time, we set stream=True
    )
    if stream:
        aml_response = AMLResponse(response_to_dict(response), 200)
        aml_response.headers["Content-Type"] = "text/event-stream"
        return aml_response
    return response

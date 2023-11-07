# Deployment Bug Bash 11/07/2023 Instructions

Welcome to the Deployment Bug Bash scheduled for 11/07/2023. Before you can start bashing, please make sure you follow these instructions to make sure you have the correct
local environment and AI Project.

## Setting Up Local Environment

In a new shell, run the following to create a virtual environment:

```
python -m venv deployment-bug-bash-env
```

To activate the enviornment on Windows, run:

```
./deployment-bug-bash-env/scripts/Activate
```

On Linux, run:

```
source ./deployment-bug-bash-env/scripts/Activate
```

After the environment is active, run:

```
pip install -r requirements.txt
```

Your local environment is now fully ready to use the deployment code!

## Creating an AI Project

An AI Resource has **already** been provisioned for your use. Create a project that's connected to this resource by running:

```
python ./scripts/create_project.py --project-name <name of your project>
```

If you run into permission issues, ping in the chat and you will be given access to the test subscription.

## Bug Template

The bug template can be found [here](https://aka.ms/aistudio/createbug).

## Test Samples

The repo is structured is structured as follows:

1. `src/chat_completion` contains a sample for deploying a chat completion function
2. `src/foundation_model` contains samples for deploying a foundation model. Within this folder, there is a separate folder for `HuggingFace`, `LLaMA`,
and `azureml` curated. Feel free to try other models in the model catalog, which can be found [here](https://int.ai.azure.com/explore/models).
4. `src/promptflow` contains a sample for deploying a promptflow. This promptflow uses the `Default_AzureOpenAI` connection. Feel free to stress
test this sample by bringing your own promptflow and/or base image.

We recommend running the samples in the following order:
1. First, try out the foundation model examples. You may or may not have enough quota for LLaMA. If it fails for that reason, please ping in the chat, but do not file a bug.
1. After you've tested out various models from the model catalog with these examples, then try deploying promptflow. For this one, you can bring your own promptflow, but please
keep in mind that connection references/deployment names must be updated to match that in the AI resource.
1. If you have time, you can try deploying the chat completion function. This is an **advanced scenario**, so please make sure the example deploys correctly and you can invoke the endpoint. You do not have to do anything else.

Please make sure to test the following in addition to running the above scripts:

1. Updating a deployment (`tags`, `properties`, `model`, etc)
1. Getting a deployment (run `client.deployments.get(<deployment_name>)`)
1. Listing deployments (run `client.deployments.list()`)
1. Deleting a deployment (run `client.deployments.delete(<deployment_name>)`)
1. Getting the keys of the deployment (run `client.deployments.get_keys(<deployment_name>)`)


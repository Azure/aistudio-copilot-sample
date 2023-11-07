# Deployment Bug Bash 11/07/2023 Instructions

Welcome to the Deployment Bug Bash scheduled for 11/07/2023. Before you can start bashing, please make sure you follow these instructions to make sure you have the correct
local environment and AI Project.

## Clone the repo

Clone the repo by running the following command:

```shell
git clone https://github.com/Azure/aistudio-copilot-sample
git checkout deployment-bug-bash-11-07
```


## Setting Up Local Environment

You will create a environment, activate it, install required packages.

### Using virtual environment

If you are using Windows, run:

```cmd
python -m venv deployment-bug-bash-env
./deployment-bug-bash-env/scripts/Activate
pip install -r requirements.txt
```

To do this on Linux, run:

```bash
python -m venv deployment-bug-bash-env
source ./deployment-bug-bash-env/scripts/Activate
pip install -r requirements.txt
```

### Using conda

Alternatively, you can use conda too:

```shell
conda create -n deployment-bug-bash-env python=3.10
conda activate deployment-bug-bash-env
pip install -r requirements.txt
```

Your local environment is now fully ready to use the deployment code!

## Creating an AI Project

An AI Resource has **already** been provisioned for your use. Create a project that's connected to this resource by following below steps:

1. Visit this [link to the AI Resource](https://int.ai.azure.com/manage/overview?wsid=/subscriptions/b17253fa-f327-42d6-9686-f3e553e24763/resourceGroups/rg-deploymentbugbash/providers/Microsoft.MachineLearningServices/workspaces/deployment_bug_bash&tid=72f988bf-86f1-41af-91ab-2d7cd011db47).
1. Click `View all` on the Project panel.
1. Click `+New Project`, enter your project name, then click `Create a project`. For your project, you can use the provided subscription and resource group but it may not have enough CPU quota that you need. In such case, use other subscription and resource group of your choice.
1. You will see the Project detail page. Click `Settings` on bottom left, then click `View in the Azure Portal` on Resource Configuration panel on top right.
1. Click `Download config.json`, then put the downloaded file into your root directory of your cloned repo.

<!--
```
python ./scripts/create_project.py --project-name <name of your project>
```

If you run into permission issues, ping in the chat and you will be given access to the test subscription.
-->

## Bug Template

The bug template can be found [here](https://aka.ms/aistudio/createbug).

## Code/API References

Reference docs are still in progress. For now, please see these files for a full list of parameters the deployment object/operations accept:

1. `client.deployments.*`: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-resources/azure/ai/resources/operations/_deployment_operations.py
1. `class Deployment`: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-resources/azure/ai/resources/entities/deployment.py
1. `class DeploymentKeys`: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-resources/azure/ai/resources/entities/deployment_keys.py
1. Model classes (`Model` and `PromptflowModel`): https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-resources/azure/ai/resources/entities/models.py 

## Test Samples

The repo is structured is structured as follows:

1. `src/chat_completion` contains a sample for deploying a chat completion function
1. `src/foundation_model` contains samples for deploying a foundation model. Within this folder, there is a separate folder for `HuggingFace`, `LLaMA`,
and `azureml` curated. Feel free to try other models in the model catalog, which can be found [here](https://int.ai.azure.com/explore/models).
1. `src/promptflow` contains a sample for deploying a promptflow. This promptflow uses the `Default_AzureOpenAI` connection. Feel free to stress
test this sample by bringing your own promptflow and/or base image.

Each sub-folder contains a `deploy.py` that will deploy the model or application code, as well as an `invoke.py` that can be used to invoke the deployment. You should
**first** use the `deploy.py` script to create the deployment. Remember to provide the deployment name as a parameter (eg `python src/foundation_model/azureml/deploy.py --deployment-name <your-deployment-name>`. Then you can use the `invoke.py` script to test the deployment.

We recommend running the samples in the following order:
1. First, try out the foundation model examples. You may or may not have enough quota for LLaMA. If it fails for that reason, please ping in the chat, but do not file a bug.
1. After you've tested out various models from the model catalog with these examples, then try deploying promptflow. For this one, you can bring your own promptflow, but please
keep in mind that connection references/deployment names must be updated to match that in the AI resource. You may also have to create connections in your project to make your
own promptflow work. Note that the path the promptflow must be a local path.
1. If you have time, you can try deploying the chat completion function. This is an **advanced scenario**, so please make sure the example deploys correctly and you can invoke the endpoint. You do not have to do anything else.

Please make sure to test the following in addition to running the above scripts:

1. Updating a deployment (`tags`, `properties`, `model`, etc)
1. Getting a deployment (run `client.deployments.get(<deployment_name>)`)
1. Listing deployments (run `client.deployments.list()`)
1. Deleting a deployment (run `client.deployments.delete(<deployment_name>)`)
1. Getting the keys of the deployment (run `client.deployments.get_keys(<deployment_name>)`)


If you run into quota issues, try passing  `instance_type="Standard_E4s_v3"` to the deployment object.
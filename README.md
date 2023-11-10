## ❗Important

**Features contained in this repository are in private preview. Preview versions are provided without a service level agreement, and they are not recommended for production workloads. Certain features might not be supported or might have constrained capabilities. For more information, see [Supplemental Terms of Use for Microsoft Azure Previews](https://azure.microsoft.com/en-us/support/legal/preview-supplemental-terms/).**

# Getting Started

This repository is part of the [Azure AI Studio preview](https://aka.ms/azureai/docs).

## Step 1: Set up your development environment

To get started quickly, you can use a pre-built development environment. **Click the button below** to open the repo in GitHub Codespaces, and then continue the readme!

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/Azure/aistudio-copilot-sample?quickstart=1)

If you want to get started in your local environment, first install the packages:
```
git clone https://github.com/azure/aistudio-copilot-sample
cd aistudio-copilot-sample
pip install -r requirements.txt
```

Then install the Azure AI CLI, on Ubuntu:
```
curl -sL https://aka.ms/InstallAzureAICLIDeb | sudo bash
```

To install the CLI on Windows and MacOS, follow the instructions [here](https://github.com/Azure/azureai-insiders/blob/main/previews/aistudio/how-to/use_azureai_sdk.md#install-the-cli).

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


## Step 6: Deploy the sample code

### LLaMA

To deploy LLaMA, run:

```python
cd src/LLaMA
python ./deploy.py
```

To invoke LLaMA, run:

```python
cd src/LLaMA
python ./invoke.py
```

### Promptflow

To deploy promptflow, run:

```python
cd src/promptflow
python ./deploy.py
```

To invoke LLaMA, run:

```python
cd src/promptflow
python ./invoke.py
```

To deploy one of the implementations to an online endpoint, use:
```bash
python src/run.py --deploy
```

To test out the online enpoint, run:
```bash
python src/run.py --invoke 
```

## Additional Tips and Resources


### Follow the full tutorial

For a more detailed tutorial using this notebook, you can follow the [Build a co-pilot using the Azure AI SDK](https://github.com/Azure/azureai-insiders/blob/aistudio-preview/previews/aistudio/tutorials/copilot_with_sdk.md) tutorial.

### Customize the development container

You can pip install packages into your development environment but they will disappear if you rebuild your container and need to be reinstalled (re-build is not automatic). You may want this, so that you can easily reset back to a clean environment. Or, you may want to install some packages by default into the container so that you don't need to re-install packages after a rebuild.

To add packages into the default container, you can update the Dockerfile in `.devcontainer/Dockerfile`, and then rebuild the development container from the command palette by pressing `Ctrl/Cmd+Shift+P` and selecting the `Rebuild container` command.

## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft 
trademarks or logos is subject to and must follow 
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.

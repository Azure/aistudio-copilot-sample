## ❗Important

**Features contained in this repository are in private preview. Preview versions are provided without a service level agreement, and they are not recommended for production workloads. Certain features might not be supported or might have constrained capabilities. For more information, see [Supplemental Terms of Use for Microsoft Azure Previews](https://azure.microsoft.com/en-us/support/legal/preview-supplemental-terms/).**

# Getting Started

This repository is part of the [Azure AI Studio preview](https://aka.ms/azureai/docs).

## Step 1: Set up your development environment

To get started quickly, we recommend to use a pre-built development environment. **Click the button below** to open the repo in GitHub Codespaces, and then continue the readme!

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/Azure/aistudio-chat-demo?quickstart=1)

Note: This will build a development environment using the Docker container definition in [.devcontainer/Dockerfile](.devcontainer/Dockerfile), and will start a VS Code instance running in that environment. 

If you want to set up your local development environment, please refer to the instructions [here](https://aka.ms/aistudio/docs/sdk) on how to manually install the Azure AI CLI and SDK on your machine.

## Step 2: Connect to Azure Resources

Login to azure and connect to an Azure AI project:

 - In VS Code, open a new terminal by pressing ```Ctrl-Shift-` ```.
 - Login to azure by typing ```az login --use-device-code``` 
 - Run ```ai init``` and select **Azure AI Project + OpenAI + Cognitive Search** to create a new Azure AI resource and project or connect to an existing project.

This will generate a config.json file in the root of the repo, the SDK will use this when authenticating to Azure AI services.

## Step 3: Run the sample notebook

Open and run the sample notebook to create, evaluate, and deploy a chatbot built using Azure OpenAI, Azure Cognitive Search, and Langchain:
 - Open the notebook: [src/langchain/langchain_qna.ipynb](src/langchain/langchain_qna.ipynb)
 - Press `Ctrl-Enter` to run each cell
    - When you run the first cell you may be prompted to select your kernel, choose `Python Environment` and select the `Python 3.10.x` environment.
 - Open your project in [AI Studio](https://aka.ms/AzureAIStudio) to view the generated indexes, evaluation runs, and endpoints.

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

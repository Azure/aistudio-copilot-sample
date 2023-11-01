## ❗Important

**Features contained in this repository are in private preview. Preview versions are provided without a service level agreement, and they are not recommended for production workloads. Certain features might not be supported or might have constrained capabilities. For more information, see [Supplemental Terms of Use for Microsoft Azure Previews](https://azure.microsoft.com/en-us/support/legal/preview-supplemental-terms/).**

# Getting Started

This repository is part of the [Azure AI Studio preview](https://aka.ms/azureai/docs).

## Step 1: Set up your development environment

To get started quickly, you can use a pre-built development environment. **Click the button below** to open the repo in GitHub Codespaces, and then continue the readme!

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/Azure/aistudio-copilot-sample/tree/oct-refresh?quickstart=1)

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

## Step 2: Create and connect to Azure Resources

Run ai init to create and/or connect to existing Azure resources:
```
ai init
```

- This will first prompt to you to login to Azure
- Then it will ask you to select or create resources, choose  **AI Project resource** and follow the prompts to create an Azure OpenAI resource, model deployments, and Azure AI  search resource
- This will generate a config.json file in the root of the repo, the SDK will use this when authenticating to Azure AI services.

Note: You can open your project in [AI Studio](https://aka.ms/AzureAIStudio) to view your projects configuration and components (generated indexes, evaluation runs, and endpoints)

## Step 3: Build an Azure Search index

Run the following CLI command to create an index that our code can use for data retrieval:
```
ai search index update --files "./data/3-product-info/*.md" --index-name "product-info"
```

Now, generate a .env file that will be used to configure the running code to use the resources we've created in the subsequent steps
```
ai dev new .env
```

## Step 4: Run the co-pilot with a sample question

To run a single question & answer through the sample co-pilot:
```bash
python src/run.py --question "which tent is the most waterproof?"
```

You can try out different sample implementations by specifying the `--implementation` flag with `promptflow`, `semantickernel`, `langchain` or `aisdk`. To try running with semantic kernel:

```bash
python src/run.py --implementation semantickernel --question "what is the waterproof rating of the tent I just ordered?"
```

To try out the promptflow implementation, double check deployment names (both embedding and chat) in `src/copilot_promptflow/flow.dag.yaml` match what's in the `.env` file.

```bash
python src/run.py --question "which tent is the most waterproof?" --implementation promptflow
```

The `--implementation` flag can be used in combination with the evaluate command below as well.

## Step 5: Test the co-pilots using chatgpt to evaluate results

To run evaluation on a copilot implementations:
```
python src/run.py --evaluate
```

You can also run pytest to run tests that use evaluation results to pass/fail
```
pytest
```

This will run the tests in `src/test_copilot.py` using the `evaluation_dataset.jsonl` as a test dataset. This will compute a set of metrics calculated by chatgpt on a 1-5 scale, and will fail that metric if the average score is less than 4.

## Step 6: Deploy the sample code

** NOT YET WORKING **

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

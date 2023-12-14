## ❗Important

**Features used in this repository are in preview. Preview versions are provided without a service level agreement, and they are not recommended for production workloads. Certain features might not be supported or might have constrained capabilities. For more information, see [Supplemental Terms of Use for Microsoft Azure Previews](https://azure.microsoft.com/en-us/support/legal/preview-supplemental-terms/).**

# Getting Started

This repository contains a copilot getting sample that can be used with the the [Azure AI Studio preview](https://aka.ms/azureai/docs). 

The sample walks through creating a copilot enterprise chat API that uses custom Python code to ground the copilot responses in your company data and APIs. The sample is meant to provide a starting point that you can further customize to add additional intelligence or capabilities. Following the below steps in the README, you will be able to: set up your development environment, create your Azure AI resources and project, build an index containing product information, run your co-pilot, evaluate it, and deploy & invoke an API.

NOTE: We do not guarantee the quality of responses produced by this sample copilot or its suitability for use in your scenario, and responses will vary as development of this sample is ongoing. You must perform your own validation the outputs of the copilot and its suitability for use within your company.

## Step 1: Set up your development environment

#### Use a pre-built development environment
To get started quickly, you can use a pre-built development environment. **Click the button below** to open the repo in GitHub Codespaces, and then continue the readme!

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/Azure/aistudio-copilot-sample?quickstart=1)

Once you've opened in Codespaces you can proceed to the next step.

#### Alternatively, set up your local development environment

First, clone the code sample locally:
```
git clone https://github.com/azure/aistudio-copilot-sample
cd aistudio-copilot-sample
```

Create a new Python virtual environment where we can safely install the SDK packages:
 * On MacOS and Linux run:
   ```
   python3 -m venv .venv
   source .venv/bin/activate
   ```
* On Windows run:
   ```
   py -3 -m venv .venv
   .venv\scripts\activate
   ```

Now that your environment is activated, install the SDK packages
```
pip install -r requirements.txt
```

Finally, install the Azure AI CLI. On Ubuntu you can use this all-in-one installer command:
```
curl -sL https://aka.ms/InstallAzureAICLIDeb | sudo bash
```

To install the CLI on Windows and MacOS, follow the instructions [here](https://aka.ms/aistudio/docs/cli).

## Step 2: Create and connect to Azure Resources

Run ai init to create and/or connect to existing Azure resources:
```
ai init
```

- This will first prompt to you to login to Azure
- Then it will ask you to select or create resources, choose  **New Azure AI Project** and follow the prompts to create an:
   - Azure AI resource
   - Azure AI project
   - Azure OpenAI Service model deployments (we recommend ada-embedding-002 for embedding, gpt-35-turbo-16k for chat, and gpt-35-turbo-16k or gpt4-32k evaluation)
   - Azure AI search resource
- This will generate a config.json file in the root of the repo, the SDK will use this when authenticating to Azure AI services.

Note: You can open your project in [AI Studio](https://aka.ms/AzureAIStudio) to view your projects configuration and components (generated indexes, evaluation runs, and endpoints)

## Step 3: Build an Azure Search index

Run the following CLI command to create an index using that our code can use for data retrieval:
```
ai search index update --files "./data/3-product-info/*.md" --index-name "product-info"
```

The ```3-product-info``` folder contains a set of markdown files with product information for the fictitious Contoso Trek retailer company. You can run this command using a different folder, or replace the contents in this folder with your own documents.

Note: if you've previously done this step and already have an index created, you can instead run ```ai config --set search.index.name <existing-index-name>```.

Now that we've created an index, we can generate a .env file that will be used to configure the running code to use the resources we've created in the subsequent steps
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

To try out the promptflow implementation, check deployment names (both embedding and chat) and index name (if it's changed from the previous steps) in `src/copilot_promptflow/flow.dag.yaml` match what's in the `.env` file.

```bash
python src/run.py --question "which tent is the most waterproof?" --implementation promptflow
```

The `--implementation` flag can be used in combination with the evaluate command below as well.

You can also use the `ai` CLI to submit a single question and/or chat interactively with the sample co-pilots, or the default "chat with your data" co-pilot:

```bash
ai chat --interactive # uses default "chat with your data" copilot
ai chat --interactive --function src/copilot_aisdk/chat:chat_completion
```

## Step 5: Test the co-pilots using chatgpt to evaluate results

To run evaluation on a copilot implementations:
```
python src/run.py --evaluate --implementation aisdk
```

You can change `aisdk` to any of the other implementation names to run an evaluation on them.

You can also use the `ai` CLI to do bulk runs and evaluations:

```bash
ai chat evaluate --input-data src/tests/evaluation_dataset.jsonl # uses default "chat with your data" copilot
ai chat evaluate --input-data src/tests/evaluation_dataset.jsonl --function src/copilot_aisdk/chat:chat_completion
```

You can also run all of the evaluations using pytest, and where tests will fail if the metrics are less than 4:
```
pytest
```

This will run the tests named `src/test_copilot_<implementation>.py` using the `evaluation_dataset.jsonl` as a test dataset. This will compute a set of metrics calculated by chatgpt on a 1-5 scale, and will fail that metric if the average score is less than 4. Not all tests are currently passing (this is expected as we work to improve the sample copilot implementations).

## Step 6: Deploy the sample code

To deploy one of the implementations to an online endpoint, use:
```bash
python src/run.py --deploy
```

To test out the online enpoint, run:
```bash
python src/run.py --invoke 
```

## Additional Tips and Resources

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

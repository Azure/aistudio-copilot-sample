### ❗Important

**Features used in this repository are in preview. Preview versions are provided without a service level agreement, and they are not recommended for production workloads. Certain features might not be supported or might have constrained capabilities. For more information, see [Supplemental Terms of Use for Microsoft Azure Previews](https://azure.microsoft.com/support/legal/preview-supplemental-terms/).**

# Getting Started

This repository contains a copilot getting sample that can be used with the the [Azure AI Studio preview](https://aka.ms/azureai/docs). 

The sample walks through creating a copilot enterprise chat API that uses custom Python code to ground the copilot responses in your company data and APIs. The sample is meant to provide a starting point that you can further customize to add additional intelligence or capabilities. Following the below steps in the README, you will be able to: set up your development environment, create your Azure AI resources and project, build an index containing product information, run your co-pilot, evaluate it, and deploy & invoke an API.

NOTE: We do not guarantee the quality of responses produced by this sample copilot or its suitability for use in your scenario, and responses will vary as development of this sample is ongoing. You must perform your own validation the outputs of the copilot and its suitability for use within your company.

## Step 1: Set up your development environment

### Step 1a: Use a cloud development environment
#### Explore sample with Codespaces
- To get started quickly with this sample, you can use a pre-built Codespaces development environment. **Click the button below** to open this repo in GitHub Codespaces, and then continue the readme!
[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/Azure/aistudio-copilot-sample?quickstart=1)

- Once you've launched Codespaces you can proceed to step 2.

#### Start developing in an Azure AI curated VS Code development environment
- If you intend to develop your own code following this sample, we recommend you use the **Azure AI curated VS Code development environment**. It comes preconfigured with the Azure AI SDK packages that you will use to run this sample.
- You can get started with this cloud environment from the Azure AI Studio by following these steps: [Work with Azure AI projects in VS Code](https://learn.microsoft.com/azure/ai-studio/how-to/develop-in-vscode)

:grey_exclamation: **Important: If you are viewing this README from within this cloud VS Code environment, you can proceed directly to step 2!** This case will apply to you if you launched VS Code from an Azure AI Studio project. The AI SDK packages are already installed.


### Step 1b: Alternatively, set up your local development environment

1. First, clone the code sample locally:
```
git clone https://github.com/azure/aistudio-copilot-sample
cd aistudio-copilot-sample
```

2. Next, create a new Python virtual environment where we can safely install the SDK packages:

 * On MacOS and Linux run:
   ```
   python3 --version
   python3 -m venv .venv
   ```
   ```
   source .venv/bin/activate
   ```
* On Windows run:
   ```
   py -3 --version
   py -3 -m venv .venv
   ```
   ```
   .venv\scripts\activate
   ```

3. Now that your environment is activated, install the SDK packages
```
pip install -r requirements.txt
```

## Step 2: Build an Azure AI Search index
In order to retrieve our product data through code, you'll create a search index. The ```3-product-info``` folder contains a set of markdown files with product information for the fictitious Contoso Trek retailer company.In the run.py, you'll see an argument for --build-index, which will create a Azure Search index via the SDK. If you want to follow this sample directly, follow the steps below. You can also run this command using a different folder of data, or replace the contents of the folder with your own documents.

In the run.py file, find where the method `build_cogsearch_index` is invoked, and specify your index name and dataset path. The method invocation should look like this:
```python
build_cogsearch_index("product-info", "./data/3-product-info")
```
Then, run the following command in the command line to create the search index:

```bash
python src/run.py --build-index
```

## Step 3: Set your Azure resource environment variables

There is an example .env file in this repo, called .env.sample. This is where you will reference environment variables in the code.
Add your Azure resources connections, deployments and keys to your .env file, and then remove the "sample" part of the file name.
Also, add your new index name value to your .env file as AZURE_AI_SEARCH_INDEX_NAME. 
Now your code can reference these resources via environment variables.

Note: You can open your project in [AI Studio](https://aka.ms/AzureAIStudio) to view your projects configuration and components (generated indexes, evaluation runs, and endpoints). You can also create new resources, deployments and connections here to use in your code.

## Step 4: Run the copilot with a sample question

To run a single question & answer through the sample co-pilot:
```bash
python src/run.py --question "which tent is the most waterproof?"
```
_Note: you may see a warning about a RuntimeError; it can be safely ignored - evaluation will be unaffected. We are working to resolve this output issue._

You can try out different sample implementations by specifying the `--implementation` flag with `promptflow`, `langchain` or `aisdk`.

:grey_exclamation: If you try out the `promptflow` implementation, first check that your deployment names (both embedding and chat) and index name (if it's changed from the previous steps) in `src/copilot_promptflow/flow.dag.yaml` match what's in the `.env` file.

```bash
python src/run.py --question "which tent is the most waterproof?" --implementation promptflow
```

## Step 5: Test the copilots using a chat completion model to evaluate results

To run evaluation on a copilot implementations:
```
python src/run.py --evaluate --implementation aisdk
```

You can change `aisdk` to any of the other implementation names to run an evaluation on them.

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
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.

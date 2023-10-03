# TODO: Neehar help implement

model = Model(
    path="./my_model_dir",
    conda_file="conda.yaml" # relative to model path if given
    model_loader_module="model_loader" # can be a file in the model directory or a module from conda dependencies
)

deployment_environment_variables = {
    "OPENAI_API_KEY": "azureml://connections/Default_AzureOpenAI/credentials/OPENAI_API_KEY",
    "OPENAI_API_BASE": "azureml://connections/connections/Default_AzureOpenAI/target",
    "OPENAI_API_VERSION": "azureml://connections/Default_AzureOpenAI/metadata/OPEN_AI_API_VERSION",
    ...
}

deployment = Deployment(
    name="my_custom_deployment",
    model=model,
    environment_variables=deployment_environment_variables,
    enable_data_collector=False,
    instance_type="Standard_DS3_v2",
)

client.deployments.create_or_update(deployment)

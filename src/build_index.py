import os

from azure.ai.generative import AIClient
from azure.identity import DefaultAzureCredential

from azure.ai.generative.operations._index_data_source import LocalSource, ACSOutputConfig
from azure.ai.generative.functions.build_mlindex import build_mlindex

# build the index using the product catalog docs from data/3-product-info
def build_cogsearch_index(index_name, path_to_data):
    client = AIClient.from_config(DefaultAzureCredential())
    index = build_mlindex(
        output_index_name=index_name,
        vector_store="azure_cognitive_search",
        embeddings_model = f"azure_open_ai://deployment/{os.environ['AZURE_OPENAI_EMBEDDING_DEPLOYMENT']}/model/{os.environ['AZURE_OPENAI_EMBEDDING_MODEL']}",
        data_source_url="https://product_info.com",
        index_input_config=LocalSource(input_data=path_to_data),
        acs_config=ACSOutputConfig(
            acs_index_name=index_name,
        ),
    )

    # register the index so that it shows up in the project
    client.mlindexes.create_or_update(index)
    
if __name__ == "__main__":
    from run import init_environment
    init_environment(None)
    build_cogsearch_index("contoso_product_index", "data/3-product_info")




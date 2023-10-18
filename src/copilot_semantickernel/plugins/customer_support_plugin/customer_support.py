from semantic_kernel.skill_definition import (
    sk_function,
)
import openai
import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import AzureTextEmbedding, AzureChatCompletion
from semantic_kernel.connectors.ai.complete_request_settings import CompleteRequestSettings
from azure.search.documents.aio import SearchClient
from azure.core.credentials import AzureKeyCredential

from api import get_customer_info

import os

class CustomerSupport:
    def __init__(self, number_of_docs, embedding_model_deployment, chat_model_deployment, temperature=0.5):
        self.number_of_docs = number_of_docs
        self.embedding_model_deployment = embedding_model_deployment
        self.chat_model_deployment = chat_model_deployment
        self.temperature = temperature

    @sk_function(
        description="See what was previously purchased by a customer. If you need more detail after using this function about a product, use the CustomerSupport.AskAboutProducts function.",
        name="GetPastOrders",
        input_description="The ID of the customer to retreive order information about"
    )
    def GetPastOrders(self, input: str) -> str:
        return str(get_customer_info(int(input))["orders"])

    @sk_function(
        description="Use this function to get additional information about a product. You may also use this function to ask generic questions about multiple products at the same time (e.g., ""what product is the best?"")",
        name="AskAboutProducts",
        input_description="The question about the products; include as many details as possible in the question",
    )
    async def AskAboutProducts(self, question: str) -> str:
        #  retrieve documents relevant to the user's question from Cognitive Search
        search_client = SearchClient(
            endpoint=os.environ["AZURE_AI_SEARCH_ENDPOINT"],
            credential=AzureKeyCredential(os.environ["AZURE_AI_SEARCH_KEY"]),
            index_name=os.environ["AZURE_AI_SEARCH_INDEX_NAME"])

        # generate a vector embedding of the user's question
        embedding = await openai.Embedding.acreate(input=question,
            model=os.environ["AZURE_OPENAI_EMBEDDING_MODEL"],
            deployment_id=os.environ["AZURE_OPENAI_EMBEDDING_DEPLOYMENT"])
        query_vector = embedding["data"][0]["embedding"]

        chunks = ""   
        async with search_client:           
            # use the vector embedding to do a vector search on the index
            results = await search_client.search(question, top=self.number_of_docs,
                    vector=query_vector, vector_fields="Embedding")

            async for result in results:
                chunks += f"\n>>> From: {result['Id']}\n{result['Text']}"  

        # Initialize a kernel so we can get the answer from the context
        kernel = sk.Kernel()
        kernel.add_chat_service(
            "chat_completion",
            AzureChatCompletion(
                self.chat_model_deployment,
                os.getenv("OPENAI_API_BASE"),
                os.getenv("OPENAI_API_KEY"),
            )
        )
    
        # Import the chat plugin from the plugins directory.
        plugins_directory = os.path.dirname(os.path.realpath(__file__)) + "/../../plugins"

        chat_plugin = kernel.import_semantic_skill_from_directory(
            plugins_directory, "chat_plugin"
        )

        # Set context variables
        variables = sk.ContextVariables()
        variables["question"] = question
        variables["context"] = chunks

        # Change temperature of qna semantic function for evaluations
        chat_plugin["qna"].set_ai_configuration(settings = CompleteRequestSettings(
            temperature=self.temperature
        ))

        # Run the qna function with the right temperature and context.
        result = await (
            kernel.run_async(chat_plugin["qna"], input_vars=variables)
        )

        return result.result
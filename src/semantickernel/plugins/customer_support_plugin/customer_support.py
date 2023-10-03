from semantic_kernel.skill_definition import (
    sk_function,
)
import openai
import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import AzureTextEmbedding, AzureChatCompletion
from semantic_kernel.connectors.ai.complete_request_settings import CompleteRequestSettings
from azure.search.documents.aio import SearchClient
from azure.core.credentials import AzureKeyCredential
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
    )
    def GetPastOrders(self) -> str:
        # TODO: Replace with an call to a mock API
        return """
        order_number: 1 
        date: 2023-01-05 
        item:
        - description:  TrailMaster X4 Tent, quantity 2, price $500 
          item_number: 1 

        order_number: 19 
        date: 2023-01-25 
        item:
        - description:  BaseCamp Folding Table, quantity 1, price $60 
          item_number: 5 

        order_number: 29 
        date: 2023-02-10 
        item:
        - description:  Alpine Explorer Tent, quantity 2, price $700 
          item_number: 8 

        order_number: 41 
        date: 2023-03-01 
        item:
        - description:  TrekMaster Camping Chair, quantity 1, price $50 
          item_number: 12 

        order_number: 50 
        date: 2023-03-16 
        item:
        - description:  SkyView 2-Person Tent, quantity 2, price $400 
          item_number: 15 

        order_number: 59 
        date: 2023-04-01 
        item:
        - description:  TrekStar Hiking Sandals, quantity 1, price $70 
          item_number: 18 
        """

    @sk_function(
        description="Use this function to get additional information about a product. You may also use this function to ask generic questions about multiple products at the same time (e.g., ""what product is the best?"")",
        name="AskAboutProducts",
        input_description="The question about the products; include as many details as possible in the question",
    )
    async def AskAboutProducts(self, question: str) -> str:
        #  retrieve documents relevant to the user's question from Cognitive Search
        search_client = SearchClient(
            endpoint=os.environ["AZURE_COGNITIVE_SEARCH_TARGET"],
            credential=AzureKeyCredential(os.environ["AZURE_COGNITIVE_SEARCH_KEY"]),
            index_name=os.environ["AZURE_SEARCH_INDEX_NAME"])

        # generate a vector embedding of the user's question
        embedding = await openai.Embedding.acreate(input=question,
            model=os.environ["AZURE_OPENAI_EMBEDDING_MODEL"],
            deployment_id=os.environ["AZURE_OPENAI_EMBEDDING_DEPLOYMENT"])
        query_vector = embedding["data"][0]["embedding"]

        context = ""   
        async with search_client:           
            # use the vector embedding to do a vector search on the index
            results = await search_client.search(question, top=self.number_of_docs,
                    vector=query_vector, vector_fields="content_vector_open_ai")

            async for result in results:
                context += f"\n>>> From: {result['sourcepage']}\n{result['content']}"  

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
        variables["context"] = context

        # Change temperature of qna semantic function for evaluations
        chat_plugin["qna"].set_ai_configuration(settings = CompleteRequestSettings(
            temperature=self.temperature
        ))

        # Run the qna function with the right temperature and context.
        result = await (
            kernel.run_async(chat_plugin["qna"], input_vars=variables)
        )
                
        return result.result
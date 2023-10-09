from langchain import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.chat_models import AzureChatOpenAI
from azure.identity import DefaultAzureCredential
from azure.ai.generative import AIClient
from azureml.rag.mlindex import MLIndex
    
async def chat_completion(messages: list[dict], stream: bool = False, 
    session_state: Any = None, extra_args: dict[str, Any] = {}):  

    question = messages[-1]["content"]
    llm = AzureChatOpenAI(
        deployment_name=os.environ.get("AZURE_OPENAI_CHAT_DEPLOYMENT"),
        model_name="gpt-35-16k-turbo",
        temperature=extra_args.get('temperature', 0.7)
    )

    template = """
    System:
    You are an AI assistant helping users with queries related to outdoor outdooor/camping gear and clothing.
    Use the following pieces of context to answer the questions about outdoor/camping gear and clothing as completely, correctly, and concisely as possible.
    If the question is not related to outdoor/camping gear and clothing, just say Sorry, I only can answer question related to outdoor/camping gear and clothing. So how can I help? Don't try to make up an answer.
    If the question is related to outdoor/camping gear and clothing but vague ask for clarifying questions.
    Do not add documentation reference in the response.

    {context}

    ---

    Question: {question}

    Answer:"
    """
    prompt_template = PromptTemplate(
        template=template,
        input_variables=["context", "question"]
    )

    # connects to project defined in the config.json file at the root of the repo
    client = AIClient.from_config(DefaultAzureCredential())

    # convert MLIndex to a langchain retriever
    index_langchain_retriever = MLIndex(
        client.mlindexes.get(name="product-info-cog-search-index", label="latest").path,
    ).as_langchain_retriever()

    qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=index_langchain_retriever,
        return_source_documents=True,
        chain_type_kwargs={
            "prompt": prompt_template,
        }
    )

    response = qa(question)
    return response["result"]
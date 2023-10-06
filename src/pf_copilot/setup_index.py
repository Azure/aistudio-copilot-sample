import os, shutil
from langchain.document_loaders import UnstructuredMarkdownLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores.chroma import Chroma
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain.llms import AzureOpenAI
from azure.ai.generative import AIClient
from azure.identity import DefaultAzureCredential
from consts import embeddings_model_deployment, persist_directory

def setup_credentials():
    client = AIClient.from_config(DefaultAzureCredential())
    default_aoai_connection = client.get_default_aoai_connection()
    default_aoai_connection.set_current_environment()

def _remove_persist_directory():
    if os.path.exists(persist_directory):
        shutil.rmtree(persist_directory)

def create_vectorstore(res_path: str) -> VectorStoreIndexWrapper:
    _remove_persist_directory()

    loaders = []
    for file_name in os.listdir(res_path):
        markdown_path = os.path.join(res_path, file_name)
        loader = UnstructuredMarkdownLoader(markdown_path)
        loaders.append(loader)

    vectorstoreIndexCreator = VectorstoreIndexCreator(vectorstore_kwargs={"persist_directory": persist_directory})
    vectorstoreIndexCreator.embedding = OpenAIEmbeddings(chunk_size=16) 
    return vectorstoreIndexCreator.from_loaders(loaders)

def verify(index: VectorStoreIndexWrapper, query: str) -> str:
    llm = AzureOpenAI(deployment_name=embeddings_model_deployment, temperature=0, verbose=True)
    return index.query(query, llm=llm)

def query_vectorstore(query: str) -> str:
    embeddings = OpenAIEmbeddings(chunk_size=16)
    vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
    from langchain.llms import AzureOpenAI 
    llm = AzureOpenAI(deployment_name=embeddings_model_deployment, temperature=0, verbose=True)
    chain = RetrievalQA.from_chain_type(llm, retriever=vectorstore.as_retriever())
    return chain.run(query)

setup_credentials()
index = create_vectorstore(res_path="../../data/3-product-info/")
result = verify(index, "What is the first feature?")
print(result)
result = query_vectorstore("What is the forth step?")
print(result)

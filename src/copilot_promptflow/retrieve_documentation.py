from typing import List
from promptflow import tool
from azure.search.documents import SearchClient
from azure.search.documents.models import RawVectorQuery
from azure.core.credentials import AzureKeyCredential
from promptflow.connections import CognitiveSearchConnection

@tool
def retrieve_documentation(question: str, index_name: str, embedding: List[float], search: CognitiveSearchConnection) -> str:
  
    search_client = SearchClient(endpoint=search.api_base, 
                                index_name=index_name, 
                                credential=AzureKeyCredential(search.api_key))
  
    vector_query = RawVectorQuery(vector=embedding, k=2, fields="Embedding")
    results = search_client.search(search_text="",
            vector_queries=[vector_query],
            select=["Id", "Text"])

    docs = [{"id": doc["Id"],  "text": doc["Text"]}
          for doc in results]
  
    return docs
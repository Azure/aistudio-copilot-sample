from typing import List
from promptflow import tool
from azure.search.documents import SearchClient
from azure.search.documents.models import Vector
from azure.core.credentials import AzureKeyCredential
from promptflow.connections import CognitiveSearchConnection

@tool
def retrieve_documentation(question: str, index_name: str, embedding: List[float], search: CognitiveSearchConnection) -> str:
  
  search_client = SearchClient(endpoint=search.api_base, 
                                index_name=index_name, 
                                credential=AzureKeyCredential(search.api_key))
  
  results = search_client.search(
      question, 
      top=2, 
      vector=embedding,
      vector_fields="Embedding")

  docs = [{"id": doc["id"],  "title": doc["title"], "content": doc["content"], "url": doc["sourcepage"]}
          for doc in results]
  
  return docs
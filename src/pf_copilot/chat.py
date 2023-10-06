from typing import Any, List, Dict, Union, Generator

default_prompt_text = """
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

def chat_completion(
    messages: List[dict],
    stream: bool = False,
    session_state: Any = None,
    extra_args: Dict[str, Any] = {}
) -> Union[Dict[str, Any], Generator[Dict[str, Any], None, None]]:
    question = messages[-1]["content"]

    from langchain import PromptTemplate
    from langchain.chains import RetrievalQA
    from langchain.chat_models import AzureChatOpenAI
    from langchain.embeddings.openai import OpenAIEmbeddings
    from langchain.vectorstores.chroma import Chroma
    from consts import chat_model_deployment, model_name, key_prompt_text, persist_directory

    prompt_text = extra_args[key_prompt_text]
    prompt_template = PromptTemplate(
        template=prompt_text if len(prompt_text) > 0 else default_prompt_text,
        input_variables=["context", "question"]
    )

    llm = AzureChatOpenAI(
        deployment_name=chat_model_deployment,
        model_name=model_name,
    )

    embeddings = OpenAIEmbeddings(chunk_size=16)
    vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
    qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(),
        return_source_documents=True,
        chain_type_kwargs={
            "prompt": prompt_template,
        }
    )

    response = qa(question)
    return response["result"]
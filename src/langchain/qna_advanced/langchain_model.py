from langchain import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.chat_models import AzureChatOpenAI
from azureml.rag.mlindex import MLIndex

class LangchainModel:
    def __init__(self, path):
        self.path = path
        self.mlindex = MLIndex(f"{self.path}/mlindex")

    def qna(self, question, temperature=0.0, number_of_docs=5, prompt_template=None):

        llm = AzureChatOpenAI(
            deployment_name="gpt-35-turbo-16k",
            model_name="gpt-35-16k-turbo",
            temperature=temperature,
        )

        default_template = """
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
            template=prompt_template if prompt_template is not None else default_template ,
            input_variables=["context", "question"]
        )

        qa = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=self.mlindex.as_langchain_retriever(
                search_kwargs={"k": number_of_docs}
            ),
            return_source_documents=True,
            chain_type_kwargs={
                "prompt": prompt_template,
            }
        )

        response = qa(question)

        return {
            "question": response["query"],
            "answer": response["result"],
            "context": "\n\n".join([doc.page_content for doc in response["source_documents"]])
        }

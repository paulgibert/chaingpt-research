from typing import List
from langchain.vectorstores import Chroma
from langchain.schema.document import Document
from langchain.embeddings.openai import OpenAIEmbeddings


class DocumentationStore:
    def __init__(self, db):
        self.db = db

    def query(self, query: str, num_results=5) -> List[str]:
        docs_list = self.db.similarity_search(query, k=num_results)
        return [doc.page_content for doc in docs_list]
    
    def query_description(self) -> str:
        pass

    def query_license(self) -> str:
        pass
def _store_lookup(docs: List[Document], query: str) -> str:
    """
    Build a vector store from documents and perform a query.
    """
    db = Chroma.from_documents(docs, OpenAIEmbeddings())
    docs = db.similarity_search(query)
    return docs[0].page_content
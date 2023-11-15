"""
Vectorstore tools for reading large files that are too big for
the context window.
"""

from typing import List
import os
from langchain.vectorstores import Chroma
from langchain.schema.document import Document
from langchain.embeddings.openai import OpenAIEmbeddings
from .utils import check_language, split_file


CHUNK_SIZE = 3000
CHUNK_OVERLAP = 100


def _store_lookup(docs: List[Document], query: str) -> str:
    """
    Build a vector store from documents and perform a query.
    """
    db = Chroma.from_documents(docs, OpenAIEmbeddings())
    docs = db.similarity_search(query)
    return docs[0].page_content


def vstore_and_read(path: str, query: str,
                    language: str=None) -> str:
    """
    Splits a file into chunks based off the provided language
    and creates a vectorstore. This store is queried and the
    most relevant chunk is returned.
    """
    if not os.path.exists(path):
        raise FileNotFoundError
    if language is not None:
        check_language(language)
    if language == "text":
        language = None # Do nothing for language=text
    docs = split_file(path, chunk_size=CHUNK_SIZE,
                      chunk_overlap=CHUNK_OVERLAP,
                      language=language)
    return _store_lookup(docs, query)

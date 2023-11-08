from typing import List
import os
from langchain.vectorstores import Chroma
from langchain.schema.document import Document
from langchain.embeddings.openai import OpenAIEmbeddings
from .utils import check_language, split_file


CHUNK_SIZE = 3000
CHUNK_OVERLAP = 100


def _store_lookup(docs: List[Document], query: str) -> str:
    db = Chroma.from_documents(docs, OpenAIEmbeddings())
    docs = db.similarity_search(query)
    return docs[0].page_content


def file_store_lookup_text(path: str, query: str) -> str:
    """
    Splits the contents of a text-based file located at the provided
    path into chunks that are stored in a vectorstore.
    After splitting, a query is applied to the store and
    the top matching chunk is returned. Queries should be
    carefully crafted to extract the desired information.
    Usefull for extracting important information from a large
    file that cannot be retrieved via the file_read function
    due to size constraints. Because only one document chunk is
    returned you should only use this if you believe the desired
    information is condensed in the file and not dispersed throughout.
    An error is returned if the path is invalid. Note: This function
    works best with text-based files.
    """
    if not os.path.exists(path):
        return "Error: The provided path does not exist"
    
    docs = split_file(path, chunk_size=CHUNK_SIZE,
                      chunk_overlap=CHUNK_OVERLAP)
    return _store_lookup(docs, query)


def file_store_lookup_language(path: str, language: str, query: str) -> str:
    """
    Equivalent to the file_store_lookup_text function with the added
    feature of being able to supply a language. The language is used
    to more intelligently split the document than file_store_lookup_text
    would. The supported langauges are: cpp, go, java, kotlin, js, ts,
    php, proto, python, rst, ruby, rust, scala, swift, markdown, latex,
    html, sol, and csharp. In addition to the errors returned from
    file_store_lookup_text, this function will also report an error if
    an unsupported langauge is provided.
    """
    if not os.path.exists(path):
        return "Error: The provided path does not exist"
    
    err = check_language(language)
    if err is not None:
        return err
    docs = split_file(path, chunk_size=CHUNK_SIZE,
                      chunk_overlap=CHUNK_OVERLAP,
                      language=language)
    return _store_lookup(docs, query)

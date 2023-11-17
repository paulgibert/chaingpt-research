from typing import List
import os
import logging
from langchain.schema.document import Document
from langchain.schema.vectorstore import VectorStore
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
from c3po.repo import GitRepo
from c3po.llm.repo_doc_files import repo_doc_files_from_llm


COMMON_DOC_FILES = [
    "README",
    "INSTALL",
    "BUILD",
    "CONTRIBUTING",
    "LICENSE",
    "DEPENDENCIES",
    "REQUIREMENTS",
    "CHANGELOG"
]


def _compare_filenames(name1: str, name2: str) -> bool:
    """
    Compares two filenames for the string search method.
    """
    return (name1.lower() in name2.lower()) \
            or (name2.lower() in name1.lower())


def _common_doc_files_str_search(repo: GitRepo) -> List[str]:
    """
    Searches for the documentation files of the repo by checking
    for common known values.
    """
    common_files_list = []
    for dir, filename in repo.get_files():
        for common_filename in COMMON_DOC_FILES:
            if _compare_filenames(filename, common_filename):
                path = os.path.join(dir, filename)
                common_files_list.append(path)
                break
    return common_files_list


def _common_doc_files_llm(repo: GitRepo) -> List[str]:
    """
    Asks the LLM for the documentation files of the repo.
    """
    files = [os.path.join(d, f) for d, f in repo.get_files()]
    return repo_doc_files_from_llm(files)


def _common_doc_files(repo: GitRepo) -> List[str]:
    """
    Returns common documentation files.
    """
    print("TEEEESSTTT!")
    ssearch = _common_doc_files_str_search(repo)
    if len(ssearch) > 0:
        logging.info("str search found documentation in the repo: {ssearch}")
    else:
        logging.info("str search found no documentation in the repo")
    llm = _common_doc_files_llm(repo)
    if len(llm) > 0:
        logging.info("LLM found documentation in the repo: {llm}")
    else:
        logging.info("LLM found no documentation in the repo")
    return list(set(ssearch) | set(llm))


def _load_and_split_doc_file(file_path: str, chunk_size:int,
                             chunk_overlap:int) -> List[Document]:
    """
    Loads the provided file and splits it into chunks.
    """
    loader = TextLoader(file_path)
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size,
                                              chunk_overlap=chunk_overlap)
    return loader.load_and_split(splitter)


def build_documentation_store(repo: GitRepo, chunk_size: int,
                              chunk_overlap:int) -> VectorStore:
    """
    Searches the provided repo for documentation files and creates a ChromaDB
    vector store of them. Documentation is identified by searching for a few
    common, hardcoded values (such as README) in addition to asking an
    LLM. Each identified file is split into chunks with the provided size and overlap
    and added to the store.

    @param repo: A `GitRepo` object to build the store from
    @param chunk_size: Chunk size
    @param chunk_overlap: The amount contiguous chunks overlap
    @returns A `VectorStore` of document chunks
    """
    doc_files = _common_doc_files(repo)
    chunks = []
    for file in doc_files:
        chunks += _load_and_split_doc_file(file, chunk_size=chunk_size,
                                           chunk_overlap=chunk_overlap)
    return Chroma.from_documents(chunks, OpenAIEmbeddings())

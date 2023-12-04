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
from c3po.llm.makefile_summary import makefile_summary_from_llm


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

SUPPORTED_EXT = [
    ".c",
    ".cpp",	
    ".csv",	
    ".docx",	
    ".html",
    ".java",	
    ".json",	
    ".md",
    ".pdf",	
    ".php",	
    ".pptx",		
    ".py",
    ".rb",
    ".tex",	
    ".txt",	
    ".css",		
    ".jpeg",	
    ".jpg",	
    ".js",
    ".gif",	
    ".png",		
    ".tar",	
    ".ts",
    ".xlsx",		
    ".xml",
    ".zip"]

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
    if len(files) > 100:
        logging.info("Trimming %d files down to 100 for LLM", len(files))
        files = files[:100]
    return repo_doc_files_from_llm(files)


def _create_makefile_summary(doc: str) -> str:
    response = makefile_summary_from_llm(doc)
    if response.output is None:
        logging.info("Failed to summarize %s", doc)
        return None
    with open("Makefile_summary.txt", "w", encoding="utf-8") as f:
        f.write(response.output)
        logging.info("Summarized %s: %s", doc, response.output)
    return "Makefile_summary.txt"

def common_doc_files(repo: GitRepo) -> List[str]:
    """
    Returns common documentation files. Currently truncated
    to the first 10 results to to restriction of OpenAI's Assistants API.
    """
    ssearch = _common_doc_files_str_search(repo)
    if len(ssearch) > 0:
        logging.info("str search found documentation in the repo: %s", ssearch)
    else:
        logging.info("str search found no documentation in the repo")
    llm = _common_doc_files_llm(repo).output
    if len(llm) > 0:
        logging.info("LLM found documentation in the repo: %s", llm)
    else:
        logging.info("LLM found no documentation in the repo")
    out = []
    for doc in llm:
        if len(out) >= 10:
            break
        if "makefile" in doc.lower():
            fname = _create_makefile_summary(doc)
            if fname is not None:
                out.append(fname)
        elif "." in doc:
            if "." + doc.split(".")[-1] in SUPPORTED_EXT:
                out.append(doc)
                logging.info("%s has a supported extension, including", doc)
            else:
                logging.info("Excluded %s due to unsupported extension", doc)
        else:
            # Assume it is text
            doc += ".txt"
            out.append(doc)
            logging.info("%s has no extension but including", doc)
    logging.info("Using only supported extensions: %s", out)
    return out


def _load_and_split_doc_file(file_path: str, chunk_size:int,
                             chunk_overlap:int) -> List[Document]:
    """
    Loads the provided file and splits it into chunks.
    """
    loader = TextLoader(file_path)
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size,
                                              chunk_overlap=chunk_overlap)
    return loader.load_and_split(splitter)


def build_documentation_store(repo: GitRepo, chunk_size: int=2000,
                              chunk_overlap:int=250) -> VectorStore:
    """
    Searches the provided repo for documentation files and creates a ChromaDB
    vector store of them. Documentation is identified by searching for a few
    common, hardcoded values (such as README) in addition to asking an
    LLM. Each identified file is split into chunks with the provided size and overlap
    and added to the store.

    @param repo: A `GitRepo` object to build the store from
    @param chunk_size: Chunk size
    @param chunk_overlap: The amount that contiguous chunks overlap
    @returns A `VectorStore` of document chunks
    """
    doc_files = common_doc_files(repo)
    chunks = []
    for file in doc_files:
        chunks += _load_and_split_doc_file(file, chunk_size=chunk_size,
                                           chunk_overlap=chunk_overlap)
    return Chroma.from_documents(chunks, OpenAIEmbeddings())



def _readme_path(repo: GitRepo) -> str:
    """
    Searches for README files and returns the
    path of the first match.
    """
    for dir, filename in repo.get_files():
        if "readme" in filename.lower():
            return os.path.join(dir, filename)
    return None


def build_readme_store(repo: GitRepo, chunk_size: int=750,
                       chunk_overlap:int=100) -> VectorStore:
    """
    Searches the provided `GitRepo` for a README file and builds
    a ChromaDB `VectorStore`. The first identified README is split
    into chunks with the provided size and overlap and used to build
    the store.

    @param repo: A `GitRepo` object to build the store from
    @param chunk_size: Chunk size
    @param chunk_overlap: The amount that contiguous chunks overlap
    @returns A `VectorStore` of document chunks
    """
    path = _readme_path(repo)
    if path is None:
        return None
    logging.info("Found README: %s", path)
    chunks = _load_and_split_doc_file(path, chunk_size=chunk_size,
                                    chunk_overlap=chunk_overlap)
    return Chroma.from_documents(chunks, OpenAIEmbeddings())

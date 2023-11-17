import logging
from langchain.schema.vectorstore import VectorStore
from llm.repo_description import repo_description_from_llm


MAX_CONTENT_LEN = 1000


def scan_docs_for_description(package: str, version: str,
                              db: VectorStore) -> str:
    """
    Generates a description via the provided document store
    using an LLM. If the LLM fails, the user is prompted
    for a description.

    @param package: The package
    @param version: Package version
    @param db: The document `VectorStore`
    @returns A description of the package
    """
    query = "A description of the software"
    docs_list = db.similarity_search(query, k=3)
    content = "\n\n".join([doc.page_content for doc in docs_list])
    response = repo_description_from_llm(package,
                                         version,
                                         content[:MAX_CONTENT_LEN])
    desc = response.output
    if desc is None:
        logging.error(f"LLM failed to generate a description")
        desc = input(f"Failed to generate a description for version {version} of package {package}. Please provide one: ")
        logging.info(f"User provided description {desc}")
    return desc


def scan_docs_for_license(package: str, version: str,
                          db: VectorStore) -> str:
    """
    Determines the license used via the provided document store
    using an LLM. If the LLM fails, the user is prompted for
    the license.

    @param package: The package
    @param version: Package version
    @param db: The document `VectorStore`
    @returns The license in use
    """
    query = "software project license"
    docs_list = db.similarity_search(query, k=3)
    content = "\n\n".join([doc.page_content for doc in docs_list])
    response = repo_description_from_llm(package,
                                         version,
                                         content[:MAX_CONTENT_LEN])
    li = response.output
    if li is None:
        logging.error(f"LLM failed to determine the license")
        li = input(f"Failed to determine the license for version {version} of package {package}. Please provide it: ")
        logging.info(f"User provided license {li}")
    return li
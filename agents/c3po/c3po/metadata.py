import os
import logging
from langchain.schema.vectorstore import VectorStore
from c3po.llm.repo_description import repo_description_from_llm
from c3po.llm.repo_license import repo_license_from_llm
from c3po.repo import GitRepo
from c3po.store_setup import build_readme_store


MAX_CONTENT_LEN = 1000


def scan_readme_for_description(package: str, repo: GitRepo) -> str:
    """
    Generates a description from the repository's README.

    @param package: The package name
    @param repo: The `GitRepo` to describe
    @returns A description of the repository
    """
    db = build_readme_store(repo)

    if db is not None:
        query = f"What is {package}?"
        docs = db.similarity_search(query, k=3)
        logging.info("Found documentation for repository description: %s",
                    ["\n\n".join([d.page_content for d in docs])])
        
        response = repo_description_from_llm(docs)
        desc = response.output
        
        if desc is not None:
            logging.info("LLM generated description: %s", desc)
            return desc
        logging.error("LLM failed to generate a description")
    
    else:
        logging.error("Failed to build a README store. Asking user for description.")

    desc = input("Failed to generate a description. Please provide one: ")
    logging.info("User provided description %s", desc)
    
    return desc


def _license_path(repo: GitRepo) -> str:
    """
    Searches a repository for the first file
    with 'license' in it and returns its path.
    """
    for dir, filename in repo.get_files():
        if "license" in filename.lower():
            return os.path.join(dir, filename)
    return None


def scan_docs_for_license(repo: GitRepo,
                          db: VectorStore) -> str:
    """
    Determines the license used in the provided `GitRepo`.
    First attempts to read a LICENSE file with an LLM. If
    this fails, the provided document store is queried
    from licensing information before defaulting to the
    user.

    @param repo: The `GitRepo` to find the license of
    @param db: The document `VectorStore`
    @returns The license in use
    """
    path = _license_path(repo)
    if path is not None:
        logging.info("Found license %s", path)
        with open(path, "r", encoding="utf-8") as f:
            response = repo_license_from_llm(license=f.read())
            if response.output is not None:
                logging.info("LLM determined license from license file: %s",
                             response.output)
                return response.output
            logging.info("LLM failed to determine license from %s", path)

    query = "software project license"
    docs = db.similarity_search(query, k=3)
    logging.info("Found license documentation: %s",
                 "\n\n".join([d.page_content for d in docs]))
    response = repo_license_from_llm(docs=docs)
    if response.output is not None:
        logging.info("LLM determined license from docs: %s", response.output)
        return response.output
    logging.error("LLM failed to determine the license from docs")

    li = input("Failed to determine the license. Please provide it: ")
    logging.info("User provided %s", li)
    return li

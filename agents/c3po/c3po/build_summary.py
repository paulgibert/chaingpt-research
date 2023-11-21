"""
    1) Get a summary of the Makefile if it exists
    2) Query the documentation
    3) Combine 1 and 2 into a prompt to create tested build
    instructions.
    Specefically ask for step 1, 2, 3
    For each step we need a short description of what it is,
    the command to execute it, and a test to ensure it succeeded

    Give it test tools such as
    time_command()
    measure_command_output_length
    get_command_output
    binary_exists()
"""
import os
import logging
from langchain.schema.vectorstore import VectorStore
from c3po.repo import GitRepo
from c3po.llm.makefile_summary import makefile_summary_from_llm
from c3po.llm.build_summary import build_steps_from_llm


def get_makefile_path(repo: GitRepo) -> str:
    # TODO: Ask the LLM for all potential Makefiles.
    # Turn this step into a smarter analysis of any
    # relevant build files. You could summarize all of these build files
    # and query the as a vector store, or have the LLMs choose which ones
    # to read.
    file_list = repo.get_files()
    for dir, filename in file_list:
        if "Makefile" in filename:
            return os.path.join(dir, filename)
    return None


def summarize_build_steps(package: str, version: str, repo: GitRepo, db_docs: VectorStore):
    makefile_path = get_makefile_path(repo)
    makefile = None
    if makefile_path is not None:
        logging.info("Found Makefile: %s", makefile_path)
        makefile = makefile_summary_from_llm(makefile_path).output
        logging.info("Summarized Makefile: %s", makefile)
    docs = db_docs.similarity_search("Building from source", k=6)
    logging.info("Found documentation on build process: %s",
                 "\n\n".join([d.page_content for d in docs]))
    response = build_steps_from_llm(package, version, docs=docs, makefile=makefile)
    logging.info("Generated build steps: %s", response.output)
    return response.output

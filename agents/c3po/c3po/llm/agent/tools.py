import os
from c3po.repo import GitRepo
from c3po.llm.query_file import query_file_with_llm


MAX_QUERY_LEN = 100


def query_file(query: str, file_path: str) -> str:
    """
    Executes a specified query on the contents of a
    text-based documentation file located at file_path.
    This function is specifically designed for parsing
    and analyzing documentation files, not code files.
    It reads the documentation file, applies the query,
    and returns the results, accommodating various text file
    formats.
    
    Parameters

    query: A string representing the query to be executed,
           tailored for text-based documentation.
    file_path: The path to the documentation file.

    Returns

    The result of the query, which may vary in format depending
    on the query type and the content structure of the documentation
    file.
    """
    if len(query) > MAX_QUERY_LEN:
        return "The provided `query` is too long. Must be <= {MAX_QUERY_LEN} characters."
    if not os.path.exists(file_path):
        return "The provided `file_path` does not exists"
    response = query_file_with_llm(query, file_path).output
    if len(response.output) == 0:
        return "No results found for the provided `query`"
    return response.output


def test_build_commands(file_path: str) -> str:
    pass

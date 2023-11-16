from typing import List
from googlesearch import search


def repo_url_from_web_search(package: str, max_results=10) -> List[str]:
    """
    Performs a google search for the GitHub repository of
    the provided package and returns the top results.

    @param package: The package to find the repository for
    @param max_results: The maximum number of results to return
    @returns A List of the top matching urls
    """
    if max_results <= 0:
        raise ValueError("`max_results` must be > 0")
    query = f"What is the GitHub repository for {package}?"
    results = list(search(query, num_results=max_results))
    
    # Bug in googlesearch-python sometimes returns too many results
    if len(results) > max_results:
        return results[:max_results]
    return results
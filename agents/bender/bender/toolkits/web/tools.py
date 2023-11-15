from typing import List
from googlesearch import search


MAX_SEARCH_RESULTS = 10


def websearch(query: str) -> List[str]:
    """
    Returns a list of top urls from a google search
    """
    return list(search(query, num_results=MAX_SEARCH_RESULTS))
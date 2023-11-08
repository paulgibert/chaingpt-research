from typing import List
from googlesearch import search


MAX_SEARCH_RESULTS = 10


def websearch(query: str) -> List[str]:
    return list(search(query, num_results=MAX_SEARCH_RESULTS))
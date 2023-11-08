from typing import List
import logging
from .tools import websearch


MAX_DISPLAY_RESULTS = 3


def web_websearch(query: str) -> List[str]:
    """
    Performs a google search with the provided query.
    Returns the top urls from the search.
    """
    logging.info("Searching web for {query}..")
    results = websearch(query)
    if len(results) <= MAX_DISPLAY_RESULTS:
        summary = "\n\t".join(results)
    else:
        summary = "\n\t".join(results[:MAX_DISPLAY_RESULTS])
    logging.info(summary)
    return results
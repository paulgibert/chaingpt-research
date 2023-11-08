from typing import List
from langchain.agents.agent_toolkits.base import BaseToolkit
from langchain.tools.base import BaseTool, StructuredTool
from googlesearch import search


MAX_SEARCH_RESULTS = 10


def web_search(query: str) -> List[str]:
    """
    Performs a google search with the provided query.
    Returns the top urls from the search.
    """
    return list(search(query, num_results=MAX_SEARCH_RESULTS))


class WebToolkit(BaseToolkit):
    def get_tools(self) -> List[BaseTool]:
        return [
            StructuredTool.from_function(web_search)
        ]
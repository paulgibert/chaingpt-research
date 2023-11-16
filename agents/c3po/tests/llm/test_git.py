import pytest
from c3po.llm.git import repo_url_from_llm
from c3po.llm.response import LLMResponse


def test__repo_url_from_llm__knows_url():
    """
    Checks that the correct url is returned when the
    LLM knows the answer 
    """
    response = repo_url_from_llm("grype")
    assert isinstance(response, LLMResponse)
    assert response.output == "https://github.com/anchore/grype"


def test__repo_url_from_llm__does_not_know_url():
    """
    Checks that None is returned when the LLM does not
    know the url 
    """
    response = repo_url_from_llm("not-a-repo")
    assert isinstance(response, LLMResponse)
    assert response.output is None

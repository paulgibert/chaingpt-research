import pytest
from c3po.web import repo_url_from_web_search


@pytest.mark.parametrize("max_results", [1, 5, 10])
def test__repo_url_from_web_search__simple_search(max_results: int):
    """
    Checks that the correct number of results are returned for simple
    searches
    """
    results = repo_url_from_web_search("grype", max_results=max_results)
    assert len(results) > 0
    assert len(results) <= max_results


@pytest.mark.parametrize("max_results", [-3, 0])
def test__repo_url_from_web_search__invalid_max_results(max_results: int):
    """
    Checks that value for max_results <= 0 results in a
    ValueError
    """
    with pytest.raises(ValueError):
        repo_url_from_web_search("grype", max_results=max_results)
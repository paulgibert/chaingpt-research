import pytest
from c3po.llm.repo_branch_or_tag import repo_branch_or_tag_from_llm


PACKAGE = "myrepo"
TAGS = [
    "v0.1.0",
    "v0.1.1",
    "v1.0.0",
    "v1.1.1"
]
BRANCHES = [
    "main",
    "dev",
    "extended",
    "person/branch",
    "v7",
    "v1.0.0",
    "1.1.1",
    "bug1",
    "bug_1",
    "bug2",
    "bug2"
]


def test__repo_branch_or_tag_from_llm__tag_list_contains_answer():
    """
    Check that the correct answer is returned from the tag list
    """
    response = repo_branch_or_tag_from_llm(PACKAGE, "0.1.1", BRANCHES, TAGS)
    assert response.output == "v0.1.1"


def test__repo_branch_or_tag_from_llm__branch_list_contains_answer():
    """
    Check that the correct answer is returned from the branch list
    """
    response = repo_branch_or_tag_from_llm(PACKAGE, "7", BRANCHES, TAGS)
    assert response.output == "v7"


def test__repo_branch_or_tag_from_llm__both_lists_contain_answer():
    """
    Check that the correct answer is returned when both
    lists contain the answer
    """
    response = repo_branch_or_tag_from_llm(PACKAGE, "1.0.0", BRANCHES, TAGS)
    assert response.output == "v1.0.0"


def test__repo_branch_or_tag_from_llm__no_list_contains_answer():
    """
    Check that no response is given if neither list
    has the answer
    """
    response = repo_branch_or_tag_from_llm(PACKAGE, "5.2.1", BRANCHES, TAGS)
    assert response.output is None


def test__repo_branch_or_tag_from_llm__empty_tag_list():
    """
    Check that the correct answer is returned from the tag list
    when the branch list is empty.
    """
    response = repo_branch_or_tag_from_llm(PACKAGE, "0.1.1", [], TAGS)
    assert response.output == "v0.1.1"


def test__repo_branch_or_tag_from_llm__empty_branch_list():
    """
    Check that the correct answer is returned from the branch list
    when the tag list is empty.
    """
    response = repo_branch_or_tag_from_llm(PACKAGE, "7", BRANCHES, [])
    assert response.output == "v7"


def test__repo_branch_or_tag_from_llm__both_lists_empty():
    """
    Check that no response is given when both lists
    are empty
    """
    response = repo_branch_or_tag_from_llm(PACKAGE, "7", [], [])
    assert response.output is None


def test__repo_branch_or_tag_from_llm__similar_in_both_lists():
    """
    Checks that the tag is prioritized if similar answers exist in
    branch and tag lists.
    """
    response = repo_branch_or_tag_from_llm(PACKAGE, "1.1.1", BRANCHES, TAGS)
    assert response.output == "v1.1.1"


def test__repo_branch_or_tag_from_llm__similar_in_one_list():
    """
    Checks that only one value is returned if a similar answer
    is in the same list.
    """
    response = repo_branch_or_tag_from_llm(PACKAGE, "bug 1", BRANCHES, TAGS)
    assert (response.output in ["bug1", "bug_1"])


def test__repo_branch_or_tag_from_llm__duplicates():
    """
    Checks that only one value is returned if a similar answer
    is in the same list.
    """
    response = repo_branch_or_tag_from_llm(PACKAGE, "bug2", BRANCHES, TAGS)
    assert response.output == "bug2"


def test__repo_branch_or_tag_from_llm__long_lists():
    """
    Checks that a ValueError is raised if the lists
    are too long
    """
    with pytest.raises(ValueError):
        repo_branch_or_tag_from_llm(PACKAGE, "v1.0.0", BRANCHES*1000, TAGS*1000)


def test__repo_branch_or_tag_from_llm__malformed_branch():
    """
    Checks that a ValueError is raised if a tag is malformed
    """
    with pytest.raises(ValueError):
        repo_branch_or_tag_from_llm(PACKAGE, "v1.0.0", BRANCHES + ["badbranch!"], TAGS)


def test__repo_branch_or_tag_from_llm__malformed_tag():
    """
    Checks that a ValueError is raised if a tag is malformed
    """
    with pytest.raises(ValueError):
        repo_branch_or_tag_from_llm(PACKAGE, "v1.0.0", BRANCHES, TAGS + ["badtag!"])


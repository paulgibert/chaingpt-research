import pytest
from c3po.llm.repo_doc_files import repo_doc_files_from_llm, _CommaSeparatedListOutputParser


def test__CommaSeparatedListOutputParser__many_elements():
    """
    Tests parsing a list with many elements.
    """
    parser = _CommaSeparatedListOutputParser()
    assert parser.parse("1, 2, 3") == ["1", "2", "3"]


def test__CommaSeparatedListOutputParser__many_elements_trailling_comma():
    """
    Tests parsing a list with many elements and a trailing comma.
    """
    parser = _CommaSeparatedListOutputParser()
    assert parser.parse("1, 2, 3,") == ["1", "2", "3"]



def test__CommaSeparatedListOutputParser__one_element():
    """
    Tests parsing a list with only one element.
    """
    parser = _CommaSeparatedListOutputParser()
    assert parser.parse("1") == ["1"]


def test__CommaSeparatedListOutputParser__one_element_trailing_comma():
    """
    Tests parsing a list with only one element and a trailing comma.
    """
    parser = _CommaSeparatedListOutputParser()
    assert parser.parse("1,") == ["1"]


def test__CommaSeparatedListOutputParser__empty():
    """
    Tests parsing an empty list.
    """
    parser = _CommaSeparatedListOutputParser()
    assert parser.parse("") == []


def test__repo_doc_files_from_llm__single_match():
    """
    Checks that a single file is returned for one match.
    """
    file_paths = [
        "src/README",
        "banana.py",
        "project/code/utils.cpp"
    ]
    docs = repo_doc_files_from_llm(file_paths).output
    assert isinstance(docs, list)
    assert len(docs) == 1
    assert docs[0] == "src/README"


@pytest.mark.repeat(3)
def test__repo_doc_files_from_llm__many_matches():
    """
    Checks that multiple files are returned for many matches.

    Repeat this test 3 times to make sure LLM consistently
    detects significant directory name even if the file name
    does not seem relevant.
    """
    file_paths = [
        "src/README",
        "banana.py",
        "project/code/utils.cpp",
        "src/dir/another/deep/dir/DEVELOPING",
        "project/build.sh",
        "src/docs/build-docs/apple.md"
    ]
    docs = repo_doc_files_from_llm(file_paths).output
    assert isinstance(docs, list)
    assert len(docs) == 4
    assert "src/README" in docs
    assert "src/dir/another/deep/dir/DEVELOPING" in docs
    assert "project/build.sh" in docs
    assert "docs/how-to-build/sunflower.txt" in docs


def test__repo_doc_files_from_llm__no_matches():
    """
    Checks that an empty list is returned if there are
    no matches.
    """
    file_paths = [
        "banana.py",
        "project/code/utils.cpp"
    ]
    docs = repo_doc_files_from_llm(file_paths).output
    assert isinstance(docs, list)
    assert len(docs) == 0

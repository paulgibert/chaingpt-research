from typing import List
import pytest
from c3po.store_setup import _compare_filenames, _common_doc_files_str_search


@pytest.mark.parametrize("names", [("readme", "README.md"),
                                   ("README.md", "readme"),
                                   ("requirements.txt", "REQUIREMENTS")])
def test__compare_filenames__match(names: List[str]):
    """
    Checks that True is returned for matching file names.
    """
    assert _compare_filenames(*names)


def test__compare_filenames__mismatch():
    """
    Checks that False is returned for mismatching file names.
    """
    assert not _compare_filenames("README.md", "banana.txt")


class _MockGitRepo():
    """
    A mock class of `GitRepo` for testing.
    """
    def __init__(self, files: List[str]):
        self.files = files

    def get_files(self) -> List[str]:
        """
        Mocked get_files method for testing.
        """
        return self.files


def test__common_doc_files_str_search__matches():
    """
    Checks that the correct file paths are returned
    for a repo with common known documentation.
    """
    files = [("src/", "README.md"),
             (".", "random.c")]
    repo = _MockGitRepo(files)
    docs = _common_doc_files_str_search(repo)
    assert len(docs) == 1
    assert docs[0] == "src/README.md"
    

def test__common_doc_files_str_search__no_matches():
    """
    Checks that an empty list is returned
    for a repo with no common known documentation.
    """
    files = [("src/", "nope.md"),
             (".", "random.c")]
    repo = _MockGitRepo(files)
    docs = _common_doc_files_str_search(repo)
    assert len(docs) == 0


@pytest.mark.repeat(3)
def test__common_doc_files__search_and_llm_matches():
    """
    Checks that the correct file paths are returned
    when string search and an LLM identify different
    documentation files.

    Repeat this test 3 times to make sure LLM consistently
    detects significant directory name even if the file name
    does not seem relevant.
    """
    files = [("src/", "README.md"),
             (".", "random.c"),
             ("src/docs/build-docs", "apple.md")]
    repo = _MockGitRepo(files)
    docs = _common_doc_files_str_search(repo)
    assert len(docs) == 2
    assert "src/README.md" in docs
    assert "src/docs/build-docs/apple.md" in docs


def test__common_doc_files__search_only_matches():
    """
    Checks that the correct file paths are returned
    when only string search identifies documentation
    files.
    """
    # TODO: String search is sort of a black swan 
    #       precautionary feature. Can't think of any
    #       cases where string search would yield a match
    #       where the LLM fails.
    pass


@pytest.mark.repeat(3)
def test__common_doc_files__llm_only_matches():
    """
    Checks that the correct file paths are returned
    when only an LLM identifies documentation
    files.

    Repeat this test 3 times to make sure LLM consistently
    detects significant directory name even if the file name
    does not seem relevant.
    """
    files = [(".", "random.c"),
             ("src/docs/build-docs", "apple.md")]
    repo = _MockGitRepo(files)
    docs = _common_doc_files_str_search(repo)
    assert len(docs) == 1
    assert "src/docs/build-docs/apple.md" in docs


def test__common_doc_files__neither_matches():
    """
    Checks that an empty list is returned
    when neither string search nor an LLM identify
    documentation files.
    """
    files = [(".", "random.c"),
             ("src", "apple.md")]
    repo = _MockGitRepo(files)
    docs = _common_doc_files_str_search(repo)
    assert len(docs) == 0


def test__common_doc_files__empty_list():
    """
    Checks that an empty list is returned when
    no file paths are provided
    """
    files = []
    repo = _MockGitRepo(files)
    docs = _common_doc_files_str_search(repo)
    assert len(docs) == 0

import os
import shutil
import re
import pytest
from c3po.repo import clone_repo, GitRepo, GitRepoNotFoundError, MalformedGitRepoURLError, MissingLocalGitRepoError


TEST_URL = "https://github.com/anchore/grype"
TEST_RELPATH = "grype"
TMP_PATH = ".tmp"


@pytest.fixture(autouse=True)
def setup_env():
    """
    Creates a tmp directory to house the
    cloned repository. Removes directory
    on exit
    """
    # Setup
    if os.path.exists(TMP_PATH):
        shutil.rmtree(TMP_PATH)
    os.mkdir(TMP_PATH)
    os.chdir(TMP_PATH)

    yield

    # Cleanup
    os.chdir("..")
    shutil.rmtree(TMP_PATH)


def test__GitRepo_get_tags__success():
    """
    Checks that tags are successfully returned.
    Only checks the first few oldest tags
    """
    repo = clone_repo(TEST_URL)
    correct_tags = ["v0.1.0",
                    "v0.1.0-beta.1",
                    "v0.1.0-beta.10",
                    "v0.1.0-beta.11"]
    tags = repo.get_tags()
    assert isinstance(tags, list)
    assert len(tags) >= len(correct_tags)
    assert tags[:4] == correct_tags


def test__GitRepo_get_tags__missing_local_repo():
    """
    Checks that deleting the underlying local repository
    results in a MissingLocalGitRepoError
    """
    repo = clone_repo(TEST_URL)

    # Delete the underlying local repository
    shutil.rmtree(repo.relpath)

    with pytest.raises(MissingLocalGitRepoError):
        repo.get_tags()


def test__GitRepo_get_branches__success():
    """
    Checks that branches are successfully returned.
    Checks branch names against a regex
    """
    repo = clone_repo(TEST_URL)
    branch_list = repo.get_branches()
    assert isinstance(branch_list, list)
    assert len(branch_list) > 0
    pattern = r"^[a-zA-Z0-9\-_\.]+$"
    for branch in branch_list:
        assert re.search(pattern, branch) is not None


def test__GitRepo_get_branches__missing_local_repo():
    """
    Checks that deleting the underlying local repository
    results in a MissingLocalGitRepoError
    """
    repo = clone_repo(TEST_URL)

    # Delete the underlying local repository
    shutil.rmtree(repo.relpath)

    with pytest.raises(MissingLocalGitRepoError):
        repo.get_branches()


def test__clone_repo__valid_url():
    """
    Checks cloning a valid GitHub repository succeeds
    """
    repo = clone_repo(TEST_URL)
    assert isinstance(repo, GitRepo)
    assert repo.relpath == TEST_RELPATH


@pytest.mark.parametrize("url", [
    "https://github.com/anchore/grype!",
    "https://github.com/anchore!/grype",
    "https://github.com/anchore/grype/extra",
    "https://githubcom/anchore/grype",
    "http://github.com/anchore/grype",
    "https://github.com/anchore/",
    "https://github.org/anchore/grype",
    "https://GitHub.com/anchore/grype",
    "www.github.com/anchore/grype",
    "https://github.com/anchore/grype.git"
])
def test__clone_repo__malformed_url(url: str):
    """
    Checks that malformed urls result in a MalformedGitRepoError
    """
    with pytest.raises(MalformedGitRepoURLError):
        clone_repo(url)


def test__clone_repo__nonexistent_url():
    """
    Checks that a nonexistent repo at the provided
    url results in a GitRepoNotFoundError
    """
    with pytest.raises(GitRepoNotFoundError):
        clone_repo("https://github.com/no-one/nothing")


def test__clone_repo__timeout():
    """
    Checks that a clone operation that takes too
    long results in a GitCloneTimeoutError
    """
    # TODO: Implement
    pass
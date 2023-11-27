import os
import shutil
import subprocess
import re
import pytest
from pathlib import Path
from c3po.repo import clone_repo, GitRepo, GitResourceNotFoundError, MissingLocalGitRepoError
from c3po.repo.validate import check_branch_or_tag


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
pattern = r"^[a-zA-Z0-9\-_\.]+$"

def test__GitRepo_get_branches__success():
    """
    Checks that branches are successfully returned.
    Checks branch names against a regex
    """
    repo = clone_repo(TEST_URL)
    branch_list = repo.get_branches()
    assert isinstance(branch_list, list)
    assert len(branch_list) > 0
    for branch in branch_list:
        check_branch_or_tag(branch)


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


def _get_current_branch(relpath: str) -> str:
    cmd = f"cd {relpath} && git branch | grep \"* \""
    branch = subprocess.check_output(cmd, shell=True) # TODO: shell=True is dangerous
    return branch.decode("utf-8").strip("* \n")


def test__GitRepo_checkout__valid_branch():
    """
    Verify the correct branch is retrieved to
    in GitRepo.checkout()
    """
    repo = clone_repo(TEST_URL)
    branches = repo.get_branches()
    repo.checkout(branches[-1])
    curr_branch = _get_current_branch(repo.relpath)
    assert curr_branch == branches[-1]


def _get_current_tag(relpath: str) -> str:
    cmd = f"cd {relpath} && git branch | grep \"* \""
    tag = subprocess.check_output(cmd, shell=True) # TODO: shell=True is dangerous
    return tag.decode("utf-8").split(" ")[-1].strip(")\n")


def test__GitRepo_checkout__valid_tag():
    """
    Verify the correct tag is retrieved to
    in GitRepo.checkout()
    """
    repo = clone_repo(TEST_URL)
    tags = repo.get_tags()
    repo.checkout(tags[-1])
    curr_tag = _get_current_tag(repo.relpath)
    assert curr_tag == tags[-1]


def test__GitRepo_checkout__curr_branch_set():
    """
    Verify GitRepo.curr_branch_or_tag is set
    to the correct branch.
    """
    repo = clone_repo(TEST_URL)
    branches = repo.get_branches()
    repo.checkout(branches[-1])
    assert repo.curr_branch_or_tag == branches[-1]


def test__GitRepo_checkout__curr_tag_set():
    """
    Verify GitRepo.curr_branch_or_tag is set
    to the correct tag.
    """
    repo = clone_repo(TEST_URL)
    tags = repo.get_tags()
    repo.checkout(tags[-1])
    assert repo.curr_branch_or_tag == tags[-1]


def test__GitRepo_checkout__nonexistent_branch_or_tag():
    """
    Check that a GitResourceNotFoundError is raised
    which a nonexistent branch or tag is provided to
    GitRepo.checkout()
    """
    repo = clone_repo(TEST_URL)
    with pytest.raises(GitResourceNotFoundError):
        repo.checkout("not-valid")


@pytest.mark.parametrize("name", [
    "badbranch!",
    "bad123*branch",
    "bad branch",
    "malicious-branch && ls -la",
    ""
])
def test__GitRepo_checkout__malformed_branch_or_tag(name: str):
    """
    Check that a ValueError is raised if the branch or
    tag provided to GitRepo.checkout() is malformed.
    """
    repo = clone_repo(TEST_URL)
    with pytest.raises(ValueError):
        repo.checkout(name)


def test__GitRepo_checkout__missing_local_repo():
    """
    Checks that deleting the underlying local repository
    results in a MissingLocalGitRepoError
    """
    repo = clone_repo(TEST_URL)

    tags = repo.get_tags()

    # Delete the underlying local repository
    shutil.rmtree(repo.relpath)

    with pytest.raises(MissingLocalGitRepoError):
        repo.checkout(tags[-1])


def test__GitRepo_checkout__timeout():
    """
    Checks that a checkout operation that takes too
    long results in a GitOPTimeoutError
    """
    # TODO: Implement
    pass


def test__GitRepo_get_files__success():
    """
    Verifies that get_files correctly lists
    all of the files in a nested directory.
    """
    os.mkdir("repo")
    Path("repo/file1.txt").touch()
    Path("repo/file2.txt").touch()
    os.mkdir("repo/subdir")
    Path("repo/subdir/file3.txt").touch()
    repo = GitRepo("repo")
    files = repo.get_files()
    correct = [
        ("repo", "file1.txt"),
        ("repo", "file2.txt"),
        ("repo/subdir", "file3.txt")
    ]
    assert files == correct


def test__GitRepo_get_files__missing_local_repo():
    """
    Checks that deleting the underlying local repository
    results in a MissingLocalGitRepoError
    """
    repo = clone_repo(TEST_URL)

    # Delete the underlying local repository
    shutil.rmtree(repo.relpath)

    with pytest.raises(MissingLocalGitRepoError):
        repo.get_files()


def test__clone_repo__valid_url():
    """
    Checks that cloning a valid GitHub repository succeeds
    """
    repo = clone_repo(TEST_URL)
    assert isinstance(repo, GitRepo)
    assert repo.relpath == TEST_RELPATH
    assert repo.curr_branch_or_tag == "main"


def test__clone_repo__repo_exists():
    """
    Checks that cloning a valid GitHub repository succeeds
    even if a previous clone of the same repository already
    exists
    """
    repo_path = TEST_URL.split("/")[-1]
    os.mkdir(repo_path)
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
    Checks that malformed urls result in a ValueError
    """
    with pytest.raises(ValueError):
        clone_repo(url)


def test__clone_repo__nonexistent_url():
    """
    Checks that a nonexistent repo at the provided
    url results in a GitResourceNotFoundError
    """
    with pytest.raises(GitResourceNotFoundError):
        clone_repo("https://github.com/no-one/nothing")


def test__clone_repo__timeout():
    """
    Checks that a clone operation that takes too
    long results in a GitOPTimeoutError
    """
    # TODO: Implement
    pass
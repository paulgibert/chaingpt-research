from typing import List
import re
import subprocess
import os


CLONE_TIMEOUT = 60
FATAL_ERRNO = 128


class GitRepoNotFoundError(Exception):
    """
    Indicates a that the desired GitHub repository could
    not be found
    """


class MalformedGitRepoURLError(Exception):
    """
    Indicates that a GitHub repository url is
    not properly formatted
    """


class GitCloneTimeoutError(Exception):
    """
    Indicates that a clone operation timed out
    """


class MissingLocalGitRepoError(Exception):
    """
    Occurs when a GitRepo object tried to perform
    an operation but the underlying local repo no
    longer exists or is not a valid git repository
    """


class GitRepo:
    """
    Represents a locally cloned GitHub repository.
    """
    def __init__(self, relpath: str):
        """
        @param relpath: The relative path to the repository
        """
        self.relpath = relpath

    def _check_repo_exists(self):
        """
        Checks that the underlying repository still
        exists and is a git repository
        """
        if not os.path.exists(self.relpath):
            raise MissingLocalGitRepoError("Local repository at path {self.relpath} no longer exists")
        cmd = f"cd {self.relpath} && git status"
        result = subprocess.run(cmd, shell=True,
                                capture_output=True) #TODO: shell=True is dangerous
        if result == FATAL_ERRNO:
            raise MissingLocalGitRepoError("Local repository at path {self.relpath} is no longer a git repository")
    
    def get_tags(self) -> List[str]:
        """
        Returns the list of repository tags
        @returns List of tags
        @raises MissingLocalGitRepoError if the underlying local repository
                no longer exists or is not a git repository
        """
        self._check_repo_exists()
        cmd = f"cd {self.relpath} && git tag"
        tags = subprocess.check_output(cmd, shell=True) # TODO: shell=True is dangerous
        return tags.decode("utf-8").split("\n")

    def _clean_branches(self, dirty_list: List[str]) -> List[str]:
        clean_list = []
        for dirty in dirty_list:
            if "/" not in dirty:
                continue
            if "HEAD" in dirty:
                continue
            if "*" in dirty:
                continue
            clean = dirty.split("/")[-1]
            clean_list.append(clean)
        return clean_list
    
    def get_branches(self) -> List[str]:
        """
        Returns the list of repository branches
        @returns List of branches
        @raises MissingLocalGitRepoError if the underlying local repository
                no longer exists or is not a git repository
        """
        self._check_repo_exists()
        cmd = f"cd {self.relpath} && git branch -a"
        branches = subprocess.check_output(cmd, shell=True) # TODO: shell=True is dangerous
        branches = branches.decode("utf-8").split("\n")
        return self._clean_branches(branches)

    def checkout(self):
        pass

    def list_docs(self, max_depth=None) -> List[str]:
        pass


def _check_url(url: str):
    """
    Checks that the url is properly formatted
    against a regex
    """
    pattern = r"^https://github\.com/[a-zA-Z0-9\-_]+/[a-zA-Z0-9\-_]+$"
    if re.match(pattern, url) is None:
        raise MalformedGitRepoURLError


def _get_repo_name(url: str) -> str:
    """
    Extracts the name of the repository form the url
    """
    return url.split("/")[-1]


def clone_repo(url: str) -> GitRepo:
    """
    Clones a GitHub repository into the current
    working directory and returns a GitRepo
    object referencing it.

    @param url: The url of the repository
    @returns a GitRepo object referencing the cloned repository
    @raises GitRepoNotFoundError if the url does not point to a valid repository
    @raises MalformedGitRepoURLError if the url is not a properly formatted
    @raises GitCloneTimeoutError if the clone operation times out
    """
    _check_url(url)
    repo_name = _get_repo_name(url)
    cmd = f"git clone {url}"
    try:
        result = subprocess.run(cmd, shell=True,
                                capture_output=True,
                                timeout=CLONE_TIMEOUT) #TODO: shell=True is dangerous
        if result.returncode == FATAL_ERRNO:
            raise GitRepoNotFoundError(f"Failed to clone a repository at {url}")
        return GitRepo(repo_name)
    except subprocess.TimeoutExpired:
        raise GitCloneTimeoutError(f"Cloning {url} took too long")
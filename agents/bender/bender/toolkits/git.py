from typing import List
import os
import subprocess
from langchain.agents.agent_toolkits.base import BaseToolkit
from langchain.tools import BaseTool, StructuredTool
from .exceptions import RepositoryNotFoundError, GenericCloneError


BAD_HOST_ERRNO = 32768


def _git_clone(repository: str, branch_or_tag: str=None) -> str:
    cmd = "git clone"
    if branch_or_tag:
        cmd += " -b " + branch_or_tag
    cmd += " " + repository
    r = os.system(cmd)
    if r == BAD_HOST_ERRNO:
        raise RepositoryNotFoundError()
    if r != 0:
        raise GenericCloneError()
    repo_name = repository.split("/")[-1]
    repo_name = repo_name.split(".")[0]
    return repo_name


def _list_branches(repo_name: str) -> List[str]:
    cmd = f"cd {repo_name} && git branch -a"
    branches = subprocess.check_output(cmd, shell=True)
    return branches.decode("utf-8").split("\n")


def _list_tags(repo_name: str) -> List[str]:
    cmd = f"cd {repo_name} && git tag"
    tags = subprocess.check_output(cmd, shell=True)
    return tags.decode("utf-8").split("\n")


def git_list_branches_and_tags(repository: str) -> str:
    """
    Lists all of the branches and tags associated with the provided repository uri.
    If the repository does not exist an error message is returned. Useful
    for finding the source for a desired release or version. If the repository
    does not exists, an error is returned.
    """
    try:
        repo_name = _git_clone(repository)
        branches = _list_branches(repo_name)
        tags = _list_tags(repo_name)
        os.system(f"rm -rf ./{repo_name}") # TODO: Dangerous
        return ", ".join(branches + tags)
    
    except RepositoryNotFoundError as e:
        return "Error: " + str(e)
    
    except GenericCloneError as e:
        return "Error: " + str(e)


def git_clone(repository: str, branch_or_tag: str) -> str:
    """
    Clones a git repository and returns the name of the top level directory
    which may be used for constructing paths to files within the repository.
    If the repository does not exists, and error is returned.
    """
    try:
        return _git_clone(repository, branch_or_tag)
    except RepositoryNotFoundError as e:
        return "Error: " + str(e)
    except GenericCloneError as e:
        return "Error: " + str(e)

from typing import List
import os
import subprocess
from .exceptions import RepositoryNotFoundError, GenericCloneError


BAD_HOST_ERRNO = 32768


def _clone(repository: str, branch_or_tag: str=None) -> str:
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


def list_branches_and_tags(repository: str) -> str:
    repo_name = _clone(repository)
    branches = _list_branches(repo_name)
    tags = _list_tags(repo_name)
    os.system(f"rm -rf ./{repo_name}") # TODO: Dangerous, Also replace with subprocess
    return ", ".join(branches + tags)
    

def clone(repository: str, branch_or_tag: str) -> str:
    return _clone(repository, branch_or_tag)

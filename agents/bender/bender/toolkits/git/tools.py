from typing import List
import subprocess
import shutil
from .exceptions import GitFatalError


GIT_FATAL_ERRNO = 128
CLONE_TIMEOUT = 60


def _clone(repository: str, branch_or_tag: str=None) -> str:
    """
    Clones a git repo
    """
    cmd = "git clone"
    if branch_or_tag:
        cmd += " -b " + branch_or_tag
    cmd += " " + repository
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, timeout=CLONE_TIMEOUT) #TODO: shel=True is dangerous
        if r.returncode == GIT_FATAL_ERRNO:
            raise GitFatalError(r.stderr.decode("utf-8").replace("\n", ", "))
        repo_name = repository.split("/")[-1]
        repo_name = repo_name.split(".")[0]
        return repo_name
    except subprocess.TimeoutExpired:
        raise GitFatalError("git clone command failed")


def _list_branches(repo_name: str) -> List[str]:
    """
    List the branches of a git repo
    """
    cmd = f"cd {repo_name} && git branch -a"
    branches = subprocess.check_output(cmd, shell=True)
    return branches.decode("utf-8").split("\n")


def _list_tags(repo_name: str) -> List[str]:
    """
    List the tags of a git repo
    """
    cmd = f"cd {repo_name} && git tag"
    tags = subprocess.check_output(cmd, shell=True)
    return tags.decode("utf-8").split("\n")


def list_branches_and_tags(repository: str) -> str:
    """
    Returns a comma separated list of the tags and branches of a git repo
    """
    # TODO: Update this to be a checkout and switch branch instead of
    # cloning twice.
    repo_name = _clone(repository)
    branches = _list_branches(repo_name)
    tags = _list_tags(repo_name)
    shutil.rmtree(repo_name) # TODO: Dangerous
    return ", ".join(branches + tags)


def clone(repository: str, branch_or_tag: str) -> str:
    """
    Clones a git repo. Simply calls _clone
    """
    return _clone(repository, branch_or_tag)

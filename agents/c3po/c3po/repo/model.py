from typing import List, Tuple
import subprocess
import os
from .exceptions import (GitResourceNotFoundError,
                         GitOpTimeoutError,
                         MissingLocalGitRepoError)
from .validate import check_branch_or_tag
          

CHECKOUT_TIMEOUT = 15
ERRNO = 1
FATAL_ERRNO = 128


def _clean_branch_names(dirty_list: List[str]) -> List[str]:
    """
    Parses and cleans branch names from output of running
    git branch -a
    """
    clean_list = []
    for dirty in dirty_list:
        if "remotes/origin/" not in dirty:
            continue
        if "HEAD" in dirty:
            continue
        # trim "remotes/origin/"
        clean = "/".join(dirty.split("/")[2:])
        clean_list.append(clean)
    return clean_list


def _get_current_branch_or_tag(relpath: str) -> str:
    cmd = f"cd {relpath} && git branch | grep \"* \""
    bt = subprocess.check_output(cmd, shell=True) # TODO: shell=True is dangerous
    bt = bt.decode("utf-8").strip("*()\n")
    if " " in bt:
        bt = bt.split(" ")[-1]
    return bt


class GitRepo:
    """
    Represents a locally cloned GitHub repository.
    """
    def __init__(self, relpath: str):
        """
        @param relpath: The relative path to the repository
        """
        self.relpath = relpath
        self.curr_branch_or_tag = _get_current_branch_or_tag(relpath)

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
        return tags.decode("utf-8").split("\n")[:-1] # Trim last element which is an empty string left behind from splitting

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
        return _clean_branch_names(branches)

    def checkout(self, branch_or_tag: str):
        """
        Checks out the provided branch or tag.
        @param branch_or_tag: the name of the branch or tag
        @raises MissingLocalGitRepoError if the underlying local repository
                no longer exists or is not a git repository
        @raises ValueError if the branch or tag name is malformed
        @raises GitResourceNotFound if the branch or tag does not exist
        """
        self._check_repo_exists()
        check_branch_or_tag(branch_or_tag)
        cmd = f"cd {self.relpath} && git checkout {branch_or_tag}"
        try:
            result = subprocess.run(cmd, shell=True,
                                    capture_output=True,
                                    timeout=CHECKOUT_TIMEOUT) #TODO: shell=True is dangerous
            if result.returncode == ERRNO:
                raise GitResourceNotFoundError(f"No branch/tag named {branch_or_tag}")
            self.curr_branch_or_tag = branch_or_tag
        except subprocess.TimeoutExpired:
            raise GitOpTimeoutError(f"Checkout of branch/tag {branch_or_tag} took too long")

    def get_files(self) -> List[Tuple[str, str]]:
        """
        Returns a List of all files in the repository.
        Each List element is a Tuple (directory path, file name).

        @returns a List of directory, file-name Tuples
        @raises MissingLocalGitRepoError if the underlying local repository
                no longer exists or is not a git repository
        """
        # TODO: Consider implementing max_depth
        self._check_repo_exists()
        all_files = []
        for root, _, files in os.walk(self.relpath):
            all_files += [(root, f) for f in files]
        return all_files

import os
import shutil
import subprocess
from .exceptions import GitResourceNotFoundError, GitOpTimeoutError
from .model import GitRepo
from .validate import check_url


CLONE_TIMEOUT = 60
FATAL_ERRNO = 128


def get_repo_relpath(url: str) -> str:
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
    @raises GitResourceFoundError if the url does not point to a valid repository
    @raises ValueError if the url is not a properly formatted git url
    @raises GitOpTimeoutError if the clone operation times out
    """
    check_url(url)
    relpath = get_repo_relpath(url)

    # Remove the local repository if it already exists
    if os.path.exists(relpath):
        shutil.rmtree(relpath)

    cmd = f"git clone {url}"
    try:
        result = subprocess.run(cmd, shell=True,
                                capture_output=True,
                                timeout=CLONE_TIMEOUT,
                                check=False) #TODO: shell=True is dangerous
        if result.returncode == FATAL_ERRNO:
            raise GitResourceNotFoundError(f"Failed to clone a repository at {url}")
        return GitRepo(url, relpath)
    except subprocess.TimeoutExpired as e:
        raise GitOpTimeoutError(f"Cloning {url} took too long") from e

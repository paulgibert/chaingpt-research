import logging
from .tools import list_branches_and_tags, clone
from .exceptions import RepositoryNotFoundError, GenericCloneError


def _try_clone_op(op: any, repository, *args) -> str:
    try:
        return op(repository, *args)
    except RepositoryNotFoundError:
        logging.error(f"The repository {repository} was not found")
        return "Error: The repository could not be found"
    except GenericCloneError:
        logging.error(f"An unknown error occured when cloning {repository}")
        return f"Error: Failed to clone {repository}"
    

def git_list_branches_and_tags(repository: str) -> str:
    """
    Lists all of the branches and tags associated with the provided repository uri.
    If the repository does not exist an error message is returned. Useful
    for finding the source for a desired release or version. If the repository
    does not exists, an error is returned.
    """
    logging.info(f"Listing branches and tags from {repository}")
    return _try_clone_op(list_branches_and_tags, repository)
    

def git_clone(repository: str, branch_or_tag: str) -> str:
    """
    Clones a git repository and returns the name of the top level directory
    which may be used for constructing paths to files within the repository.
    If the repository does not exists, and error is returned.
    """
    logging.info(f"Cloning {repository}...")
    return _try_clone_op(clone, repository, branch_or_tag)

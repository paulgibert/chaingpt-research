import logging
from .tools import list_branches_and_tags, clone
from .exceptions import GitFatalError


def _try_clone_op(op: any, repository, *args) -> str:
    try:
        return op(repository, *args)
    except GitFatalError as e:
        logging.error(f"A fatal error occured: {str(e)}")
        return "Error: " + str(e)
    

def git_list_branches_and_tags(repository: str) -> str:
    """
    Lists all of the branches and tags associated with the provided repository uri.
    If the repository does not exist an error message is returned. Useful
    for finding the source for a desired release or version. If the repository
    does not exists, an error is returned. Try a different
    repository path if this is the case.
    """
    items = _try_clone_op(list_branches_and_tags, repository)
    items = "  ".join(items)
    logging.info(f"Listing branches and tags from {repository}\n{items}")
    return items

    

def git_clone(repository: str, branch_or_tag: str) -> str:
    """
    Clones a git repository and returns the name of the top level directory
    which may be used for constructing paths to files within the repository.
    If the repository does not exists, and error is returned. Try a different
    repository path if this is the case.
    """
    logging.info(f"Cloning {repository}...")
    return _try_clone_op(clone, repository, branch_or_tag)

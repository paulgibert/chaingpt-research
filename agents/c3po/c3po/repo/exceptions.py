class GitResourceNotFoundError(Exception):
    """
    Indicates a that the desired GitHub resource could
    not be found
    """


class GitOpTimeoutError(Exception):
    """
    Indicates that a git operation timed out
    """


class MissingLocalGitRepoError(Exception):
    """
    Occurs when a GitRepo object tried to perform
    an operation but the underlying local repo no
    longer exists or is not a valid git repository
    """

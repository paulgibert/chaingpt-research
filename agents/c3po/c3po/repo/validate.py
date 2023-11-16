import re


def check_url(url: str):
    """
    Checks that the url is properly formatted
    """
    pattern = r"^https://github\.com/[a-zA-Z0-9\-_]+/[a-zA-Z0-9\-_]+$"
    if re.match(pattern, url) is None:
        raise ValueError(f"The provided git url {url} is not properly formatted")


def check_branch_or_tag(branch_or_tag: str):
    """
    Checks that a branch or tag is properly formatted
    """
    pattern = r"^[a-zA-Z0-9_\-\./]+$"
    if re.match(pattern, branch_or_tag) is None:
        raise ValueError(f"The provided branch/tag {branch_or_tag} is not properly formatted")

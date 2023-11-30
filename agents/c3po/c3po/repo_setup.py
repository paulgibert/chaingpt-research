import logging
from yaspin import yaspin
from yaspin.spinners import Spinners
from colorama import Fore
from c3po.repo import (GitRepo,
                       GitResourceNotFoundError,
                       GitOpTimeoutError,
                       clone_repo)
from c3po.web import repo_url_from_web_search
from c3po.llm.repo_url import repo_url_from_llm
from c3po.llm.repo_branch_or_tag import repo_branch_or_tag_from_llm
from c3po.exceptions import NoResultsFromSearchError


def _try_clone(url: str) -> GitRepo:
    """
    Attempts to clone the provided url.
    """
    try:
        return clone_repo(url)
    except (GitResourceNotFoundError,
            ValueError,
            GitOpTimeoutError) as e:
        logging.error(str(e))
    return None


def _clone_repo_url_from_user(package: str) -> GitRepo:
    """
    Prompts the user for the repository url associated with
    the provided package.
    """
    prompt = f"Failed to determine GitHub repository url for {package}. Please provide it: "
    while True:
        url = input(prompt)
        logging.info("User provided url %s", url)
        repo = _try_clone(url)
        if repo is not None:
            logging.info("Cloned url %s", url)
            break
        logging.error("Failed to clone user provided url %s", url)
        prompt = f"Failed to clone {url}. Please provide a different repository url: "
    return repo


def _get_repo(package: str) -> GitRepo:
    """
    Finds and clones the GitHub repository for
    the provided package.
    """
    web_urls = repo_url_from_web_search(package)
    with yaspin(Spinners.line, text=Fore.BLUE + "\tasking GPT-4", color="blue"):
        try:
            url = repo_url_from_llm(package, web_urls).output
            if url is not None:
                logging.info("LLM proposed url %s", url)
                repo = _try_clone(url)
                if repo is not None:
                    return repo
            else:
                logging.error("LLM failed to provide a url")
        except ValueError as e:
            logging.error(str(e))

    return None
    # return _clone_repo_url_from_user(package)


def _try_checkout(branch_or_tag: str, repo: GitRepo) -> bool:
    """
    Attempts to checkout the provided branch or tag.
    """
    try:
        repo.checkout(branch_or_tag)
        return True
    except (ValueError, GitResourceNotFoundError) as e:
        logging.error(str(e))
    return False


def _branch_or_tag_from_str_search(version: str, repo: GitRepo) -> str:
    """
    Uses a simple string search to find the correct branch or tag.
    Returns the first case where `version in branch_or_tag_name`
    """
    bt_list = repo.get_branches() + repo.get_tags()
    for bt in bt_list:
        if version in bt:
            return bt
    return None


def _checkout_branch_or_tag_from_user(package: str, version: str,
                             repo: GitRepo) -> str:
    """
    Asks the user for the correct branch or tag.
    """
    prompt = f"Failed to determine branch or tag for {package} version {version}. Please provide it: "
    while True:
        bt = input(prompt)
        logging.info("User provided branch/tag %s", bt)
        if _try_checkout(bt, repo):
            logging.info("Checked out branch/tag %s", bt)
            return bt
        logging.error("Failed to checkout user provided branch/tag %s", bt)
        prompt = f"Failed to checkout {bt}. Please provide a different branch/tag: "


def _checkout_version(package: str, version: str, repo: GitRepo) -> str:
    """
    Find and checkout the correct branch or tag.
    """
    with yaspin(Spinners.line, text=Fore.BLUE + "\ttrying with string search", color="blue"):
        bt = _branch_or_tag_from_str_search(version, repo)
    if bt is not None:
        logging.info("String search yielded branch/tag %s", bt)
        if _try_checkout(bt, repo):
            logging.info("Checked out branch/tag %s", bt)
            return bt
    else:
        logging.error("String search failed to find branch/tag")
    try:
        with yaspin(Spinners.line, text=Fore.BLUE + "\tasking GPT-4", color="blue"):
            bt = repo_branch_or_tag_from_llm(package, version,
                                            branches=repo.get_branches(),
                                            tags=repo.get_tags()).output
        if bt is not None:
            logging.info("LLM proposed branch/tag %s", bt)
            if _try_checkout(bt, repo):
                return bt
        else:
            logging.error("LLM failed to suggest a branch/tag")
    except ValueError as e:
        logging.info(str(e))

    return None
    # return _checkout_branch_or_tag_from_user(package, version, repo)


def init_repository(package: str, version: str) -> GitRepo:
    """
    Clones the GitHub repository for the provided package in the
    current working directory and does a checkout of the correct
    branch for the provided version.

    The GitHub repository url is determined by
        1) Searching for urls on google
        2) Asking the LLM given the package name and url results
        3) Otherwise fail
    
    The correct branch or tag is found by
        1) Searching for tags or branches that contain the version in their name
        2) Otherwise, ask an LLM to choose from the list of branches and tags given
           the package and version
        3) Otherwise fail
    
    @param package: The package to search for and clone
    @param version: The version to checkout
    @returns The GitRepo object representing the cloned repository checked-out to
             the correct branch
    """
    print(Fore.BLUE + "Searching for GitHub repository")
    repo = _get_repo(package)
    if repo is None:
        print(Fore.RED + f"Failed to find the GitHub repository for {package}")
        return None
    print(Fore.GREEN + f"Found {repo.url}")
    print(Fore.BLUE + f"Searching for {version} branch or tag")
    branch_or_tag = _checkout_version(package, version, repo)
    if branch_or_tag is None:
        print(Fore.RED + f"Failed to identify a branch or tag for {version}")
        return None
    print(Fore.GREEN + f"Checked-out {branch_or_tag}")
    return repo

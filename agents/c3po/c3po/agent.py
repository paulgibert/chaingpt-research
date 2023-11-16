import logging
from repo import GitRepo, GitRepoNotFoundError, MalformedGitRepoURLError, GitCloneTimeoutError, clone_repo
from web import repo_url_from_web_search
from llm.git import repo_url_from_llm
from user import prompt_user


class Agent:
    def __init__(self):
        pass
    
    def _try_clone(self, url: str) -> GitRepo:
        try:
            return clone_repo(url)
        except GitRepoNotFoundError:
            logging.info(f"Failed cloning {url}. Not a valid repository")
        except MalformedGitRepoURLError:
            logging.info(f"Failed cloning {url}. Malformed url")
        except GitCloneTimeoutError:
            logging.info(f"Failed cloning {url}. Clone operation timed out")
        return None
    
    def _try_clone_from_web_search(self, package: str) -> GitRepo:
        url_list = repo_url_from_web_search(package)
        repo = None
        for url in url_list:
            repo = self._try_clone(url)
            if repo is not None:
                break
        return repo
    
    def _try_clone_from_llm(self, package: str) -> GitRepo:
        response = repo_url_from_llm(package)
        url = response.output
        if url is not None:
            return self._try_clone(url)
        logging.info(f"LLM failed to provide any url for {package}")

    def _clone_from_user_input(self, package: str) -> GitRepo:
        prompt = f"Failed to determine GitHub repository url for {package}. Please provide it: "
        while True:
            url = prompt_user(prompt)
            logging.info("User provided url {url}")
            repo = self._try_clone(url)
            if repo is not None:
                break
            prompt = f"Failed to clone {url}. Please provide a valid repository url: "
    
    def init_repo(self, package: str, version: str) -> GitRepo:
        # Search the web for the repository url
        logging.info(f"Searching web for {package} GitHub repository url")
        repo = self._try_clone_from_web_search(package)
        if repo is not None:
            return repo
        
        # Ask an LLM for the repository url
        logging.info(f"Prompting LLM for {package} GitHub repository url")
        repo = self._try_clone_from_llm(package)
        if repo is not None:
            return repo
        
        # Ask the user for the repository url
        logging.info(f"Prompting user for {package} GitHub repository url")
        return self._clone_from_user_input(package)

    def run(self, package: str, version: str):
        repo = self.init_repo(package)
import os
import shutil
import logging
from repo_setup import init_repository
from repo import GitRepo


# init_repository() -> repo
#     knows how to use repo to init repository
#     repo/

# build_documentation_store(repo) -> db
#     vstore/

# generate_metadata(repo)
#     generate/

# generate_build_description(repo)
#     generate/

# build_yaml(meta, desc)

logging.basicConfig(filename='agent.log', encoding='utf-8', level=logging.INFO)

ENV_DIR = ".tmp"


def _init_env():
    if os.path.exists(ENV_DIR):
        shutil.rmtree(ENV_DIR)
    os.mkdir(ENV_DIR)
    os.chdir(ENV_DIR)


def run_agent(package: str, version: str):
    _init_env()
    repo = init_repository(package, version)


run_agent("random-package", "0.70.0")
import os
import shutil
import logging
from c3po.repo_setup import init_repository
from c3po.repo import GitRepo
from c3po.metadata import scan_docs_for_description, scan_docs_for_license


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
    
    # db_docs = build_documentation_store(repo)
    # db_code = build_code_store(repo)

    # desc = scan_docs_for_description(db_docs)
    # license = scan_repo_for_license(repo, db_docs)
    # build_summary = summarize_build(repo, db_docs, db_code)
    # build_yaml(package, version, desc, license, build_summary)


run_agent("random-package", "0.70.0")
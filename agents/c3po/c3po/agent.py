import os
import shutil
import logging
from c3po.repo_setup import init_repository
from c3po.store_setup import build_documentation_store
from c3po.metadata import scan_readme_for_description, scan_docs_for_license
from c3po.build_summary import summarize_build_steps

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

    db_docs = build_documentation_store(repo)
    # db_code = build_code_store(repo)

    desc = scan_readme_for_description(package, repo)
    li = scan_docs_for_license(repo, db_docs)

    print(li)
    print(desc)

    build_summary = summarize_build_steps(package, version, repo, db_docs)
    print(build_summary)
    # build_yaml(package, version, desc, license, build_summary)


run_agent("grype", "0.72.0")
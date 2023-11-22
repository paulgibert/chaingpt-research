import os
import shutil
import logging
from c3po.repo_setup import init_repository
from c3po.store_setup import common_doc_files
from c3po.assistant import run_assistant


logging.basicConfig(filename='agent.log', encoding='utf-8', level=logging.INFO)

ENV_DIR = ".tmp"
ASSISTANT_ID = "asst_6f9uzyHimrjjggaKfSw5DGeG"

def _init_env():
    if os.path.exists(ENV_DIR):
        shutil.rmtree(ENV_DIR)
    os.mkdir(ENV_DIR)
    os.chdir(ENV_DIR)

def run_agent(package: str, version: str):
    _init_env()
    repo = init_repository(package, version)
    doc_file_paths = common_doc_files(repo)
    output = run_assistant(package, version, doc_file_paths)
    print(output)

run_agent("grype", "0.72.0")
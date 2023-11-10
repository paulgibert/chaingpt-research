from .model import (MelangeYaml, RunsPipeline,
                    GitCheckoutPipeline, GoBuildPipeline)
from .exceptions import MissingMelangeHeader


state = None


def _check_state_exists() -> str:
    global state
    if state is None:
        raise MissingMelangeHeader()
    return None


def add_header(package: str, version: str, description: str,
               license: str):
    #TODO: Validate license
    global state
    state = MelangeYaml(package, version, description, license)


def add_build_dependency(package: str):
    global state
    _check_state_exists()
    state.add_build_dependency(package)


def add_pipeline_runs(command: str):
    global state
    _check_state_exists()
    state.add_pipeline(RunsPipeline(command))


def add_pipeline_git_checkout(repository: str, branch: str=None,
                              tag: str=None):
    global state
    _check_state_exists()
    pipe = GitCheckoutPipeline(repository, branch, tag)
    state.add_pipeline(pipe)


def add_pipeline_go_build(packages: str, output: str,
                          modroot: str=None, prefix: str=None,
                          ldflags: str=None, install_dir: str=None):
    global state
    _check_state_exists()
    pipe = GoBuildPipeline(packages, output,
                           modroot=modroot,
                           prefix=prefix,
                           ldflags=ldflags,
                           install_dir=install_dir)
    state.add_pipeline(pipe)


def write_model():
    global state
    _check_state_exists()
    path = "tmp.yaml"
    with open(path, "w", encoding="utf-8") as f: # TODO: dangerous
        state.dump_yaml(f)
from .model import (MelangeYaml, RunsPipeline,
                    GitCheckoutPipeline, GoBuildPipeline)
from .exceptions import MissingMelangeHeader


state = None # TODO: Implement without singleton


def _check_state_exists() -> str:
    """
    Check that a melange YAML object has been initialized
    """
    if state is None:
        raise MissingMelangeHeader()
    return None


def add_header(package: str, version: str, description: str,
               license: str):
    """
    Initialize a melange YAML object
    """
    #TODO: Validate license
    global state
    state = MelangeYaml(package, version, description, license)


def add_build_dependency(package: str):
    """
    Adds a build dependency to the current melange YAML
    """
    _check_state_exists()
    state.add_build_dependency(package)


def add_pipeline_runs(command: str):
    """
    Adds a runs pipeline stage to the current melange YAML
    """
    _check_state_exists()
    state.add_pipeline(RunsPipeline(command))


def add_pipeline_git_checkout(repository: str, branch: str=None,
                              tag: str=None):
    """
    Adds a git-checkout pipeline stage to the current melange YAML
    """
    _check_state_exists()
    pipe = GitCheckoutPipeline(repository, branch, tag)
    state.add_pipeline(pipe)


def add_pipeline_go_build(packages: str, output: str,
                          modroot: str=None, prefix: str=None,
                          ldflags: str=None, install_dir: str=None):
    """
    Adds a go/build stage to the current melange YAML
    """
    _check_state_exists()
    pipe = GoBuildPipeline(packages, output,
                           modroot=modroot,
                           prefix=prefix,
                           ldflags=ldflags,
                           install_dir=install_dir)
    state.add_pipeline(pipe)


def write_model():
    """
    Writes the current melange YAML to disk
    """
    _check_state_exists()
    path = "tmp.yaml"
    with open(path, "w", encoding="utf-8") as f:
        state.dump_yaml(f)
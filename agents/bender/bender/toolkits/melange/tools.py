import os
from .model import (MelangeYaml, RunsPipeline,
                    GitCheckoutPipeline, GoBuildPipeline)


state = None


def _check_state_exists() -> str:
    global state
    if state is None:
        return "Error: Must first add a melange header."
    return None


def melange_add_header(package: str, version: str, description: str,
                       license: str):
    """
    Initializes a melange YAML model with the provided metadata.
    Calling this function multiple times will discard the previous
    model including all ascociated dependencies and pipeline steps.
    package: The name of the package
    version: The version of the package
    description: A one sentence description of the package
    license: The package's license
    """
    #TODO: Validate license
    global state
    state = MelangeYaml(package, version, description, license)


def melange_add_build_dependency(package: str):
    """
    Adds a package to the list of build-time dependencies of an
    initialized melange YAML model.
    An error is returned if no model has been initialized.
    package: The name of the package to add 
    """
    global state
    _check_state_exists()
    state.add_build_dependency(package)


def melange_add_pipeline_runs(command: str):
    """
    Adds a generic run pipeline step to an initialized
    melange YAML model. An error is returned if no model has
    been initialized. Run steps execute shell commands during
    the build process.
    command: shell command to run
    """
    global state
    _check_state_exists()
    state.add_pipeline(RunsPipeline(command))


def melange_add_pipeline_git_checkout(repository: str, branch: str=None,
                                      tag: str=None):
    """
    Adds a git-checkout pipeline step to an initialized
    melange YAML model. An error is returned if no model
    has been initialized. Git-checkout steps checkout git
    repositories, a common first step in many builds.
    repository: The git repository
    branch: The branch to checkout
    tag: The tag to checkout
    """
    global state
    _check_state_exists()
    pipe = GitCheckoutPipeline(repository, branch, tag)
    state.add_pipeline(pipe)


def melange_add_pipeline_go_build(packages: str, output: str,
                                  modroot: str=None, prefix: str=None,
                                  ldflags: str=None, install_dir: str=None):
    """
    Adds a go/build pipeline step to an initialized
    melange YAML model. An error is returned if no model
    has been initialized.Go/build steps build and install
    go projects. Use the default values when possible.
    packages: List of space-separated packages to compile. Files con also be specified.
              This value is passed as an argument to go build.
              All paths are relative to the provided modroot.
    output: Filename to use when writing the binary. The final install location inside
            the apk will be in prefix / install_dir / output
    modroot: Top directory of the go module, this is where go.mod lives. Before buiding
             the go pipeline wil cd into this directory.
    prefix: Prefix to relocate binaries. Defaults to 'usr'.
    ldflags: List of [pattern=]arg to pass to the go compiler with -ldflags
    install_dir: Directory where binaries will be installed. Defaults to 'bin'.
    """
    global state
    _check_state_exists()
    pipe = GoBuildPipeline(packages, output,
                           modroot=modroot,
                           prefix=prefix,
                           ldflags=ldflags,
                           install_dir=install_dir)
    state.add_pipeline(pipe)


def melange_write_model(path: str):
    """
    This function writes the Melange YAML model to a yaml file
    at the provided path. An error is returned if the path already
    exists. Call this function after initializing the model with a header
    and adding dependencies and pipeline steps.
    """
    global state
    _check_state_exists()
    
    if os.path.exists(path):
        return "Error: The provided path already exists."
    
    with open(path, "w", encoding="utf-8") as f: # TODO: dangerous
        state.dump_yaml(f)
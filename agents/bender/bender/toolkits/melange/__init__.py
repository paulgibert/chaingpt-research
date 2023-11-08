import logging
from .tools import (add_header,
                    add_build_dependency,
                    add_pipeline_runs,
                    add_pipeline_git_checkout,
                    add_pipeline_go_build,
                    write_model)
from .exceptions import MissingMelangeHeader


def melange_add_header(package: str, version: str, description: str,
                       license: str) -> str:
    """
    Initializes a melange YAML model with the provided metadata.
    Calling this function multiple times will discard the previous
    model including all ascociated dependencies and pipeline steps.
    package: The name of the package
    version: The version of the package
    description: A one sentence description of the package
    license: The package's license
    """
    logging.info(f"Initializing Melange YAML for {package}=={version}")
    logging.info(f"\tname: {package}, version: {version}, license: {license}, desc: {description}")
    add_header(package, version, description, license)
    return "Success"


def melange_add_build_dependency(package: str) -> str:
    """
    Adds a package to the list of build-time dependencies of an
    initialized melange YAML model.
    An error is returned if no model has been initialized.
    package: The name of the package to add 
    """
    logging.info(f"Adding dependency {package}")
    try:
        add_build_dependency(package)
    except MissingMelangeHeader:
        logging.error("No melange header is initialized")
        return "Error: Must first add a melange header."
    return "Success"


def melange_add_pipeline_runs(command: str) -> str:
    """
    Adds a generic run pipeline step to an initialized
    melange YAML model. An error is returned if no model has
    been initialized. Run steps execute shell commands during
    the build process.
    command: shell command to run
    """
    logging.info(f"Adding `runs` pipeline stage: {command}")
    try:
        add_pipeline_runs(command)
    except MissingMelangeHeader:
        logging.error("No melange header is initialized")
        return "Error: Must first add a melange header."
    return "Success"


def melange_add_pipeline_git_checkout(repository: str, branch: str=None,
                                      tag: str=None) -> str:
    """
    Adds a git-checkout pipeline step to an initialized
    melange YAML model. An error is returned if no model
    has been initialized. Git-checkout steps checkout git
    repositories, a common first step in many builds.
    repository: The git repository
    branch: The branch to checkout
    tag: The tag to checkout
    """
    logging.info(f"Adding `git/checkout` pipeline stage")
    msg = f"\trepository: {repository}"
    if branch is not None:
        msg += f", branch: {branch}"
    elif tag is not None:
        msg += f", tag: {tag}"
    logging.info(msg)
    try:
        add_pipeline_git_checkout(repository, branch, tag)
    except MissingMelangeHeader:
        logging.error("No melange header is initialized")
        return "Error: Must first add a melange header."
    return "Success"


def melange_add_pipeline_go_build(packages: str, output: str,
                                  modroot: str=None, prefix: str=None,
                                  ldflags: str=None, install_dir: str=None) -> str:
    """
    Adds a go/build pipeline step to an initialized
    melange YAML model. An error is returned if no model
    has been initialized. Go/build steps build and install
    go projects. Use the default values when possible.
    packages: Space-separated packages to compile. Files can also be specified.
              This value is passed to go build. Paths are relative to modroot.
    output: Name of the output binary. The final install location will be
            in prefix/install_dir/output
    modroot: Top directory of the go module, this is where go.mod lives. Before buiding
             the go pipeline wil cd into this directory.
    prefix: Prefix to relocate binaries. Defaults to 'usr'.
    ldflags: List of [pattern=]arg to pass to the go compiler with -ldflags
    install_dir: Directory where binaries will be installed. Defaults to 'bin'.
    """
    msg = f"\tpackages: {packages}, output: {output}"
    if modroot is not None:
        msg += f"modroot: {modroot}"
    if prefix is not None:
        msg += f"prefix: {prefix}"
    if ldflags is not None:
        msg += f"ldflags: {ldflags}"
    if install_dir is not None:
        msg += f"install_dir: {install_dir}"
    logging.info(f"Adding `go/build` pipeline stage")
    logging.info(msg)
    try:
        add_pipeline_go_build(packages, output, modroot, prefix,
                          ldflags, install_dir)
    except MissingMelangeHeader:
        logging.error("No melange header is initialized")
        return "Error: Must first add a melange header."
    return "Success"


def melange_write_model() -> str:
    """
    This function writes the Melange YAML model.
    Call this function after initializing the model with a header
    and adding dependencies and pipeline steps.
    """
    logging.info(f"Done constructing YAML. Writing to file...")
    try:
        write_model()
    except MissingMelangeHeader:
        logging.error("No melange header is initialized")
        return "Error: Must first add a melange header."
    logging.info(f"Success!")
    return "Success"
    
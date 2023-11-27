from typing import List
from sh import melange, ErrorReturnCode_1
from .utils import append_arg, arg_to_strings


WOLFI_KEYRING = "https://packages.wolfi.dev/os/wolfi-signing.rsa.pub"
WOLFI_REPOSITORY = "https://packages.wolfi.dev/os"


def melange_build(yaml_file: str,
                  out_dir="packages",
                  log_file: str="build.log",
                  keyring_append: List[str] | str=None,
                  repository_append: List[str] | str=None,
                  arch: List[str] | str=None):
    """
    Builds a package for the given melange file.

    @param yaml_file: The melange yaml file
    @param out_dir: The directory to output the built packages
    @param log_file: The name of the log file for the build
    @param keyring_append: Keyrings for the build. Passed to --keyring-append.
    @param repository_append: Repositories for the build. Passed to --keyring-append.
    """
    key_strings = arg_to_strings(keyring_append)
    repo_strings = arg_to_strings(repository_append)
    arch_strings = arg_to_strings(arch)

    try:
        melange("build", yaml_file,
                out_dir=out_dir,
                keyring_append=key_strings,
                repository_append=repo_strings,
                arch=arch_strings,
                _err=log_file)
    except ErrorReturnCode_1:
        # Swallow melange errors here and refer to the log file
        pass


def melange_build_wolfi(yaml_file: str,
                        out_dir="packages",
                        log_file: str="build.log",
                        keyring_append: List[str] | str=None,
                        repository_append: List[str] | str=None,
                        arch: List[str] | str=None):
    """
    Builds a package for the given melange file with the Wolfi keyring and
    repository appended.

    @param yaml_file: The melange yaml file
    @param out_dir: The directory to output the built packages
    @param log_file: The name of the log file for the build
    @param keyring_append: Keyrings for the build. Passed to --keyring-append.
    @param repository_append: Repositories for the build. Passed to --keyring-append.
    """
    keys = append_arg(WOLFI_KEYRING, keyring_append)
    repos = append_arg(WOLFI_REPOSITORY, repository_append)

    melange_build(yaml_file,
                  out_dir=out_dir,
                  log_file=log_file,
                  keyring_append=keys,
                  repository_append=repos,
                  arch=arch)

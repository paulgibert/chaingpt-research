from typing import List
import os
import shutil
from sh import melange, ErrorReturnCode_1
from .utils import arg_to_strings
from .exceptions import MelangeBuildError


WOLFI_KEYRING = "https://packages.wolfi.dev/os/wolfi-signing.rsa.pub"
WOLFI_REPOSITORY = "https://packages.wolfi.dev/os"


# def _melange_build(yaml_file: str,
#                    log_file: str,
#                    signing_key: str,
#                    keyring_append: str=None,
#                    repository_append: str=None,
#                    arch: str=None):
#     """
#     Wraps a docker container around the melange
#     build command.
#     """
#     try:
#         docker("run", "--privileged",
#                "-v", ".:/work",
#                "--entrypoint=melange",
#                "--workdir=/work",
#                "ghcr.io/wolfi-dev/sdk",
#                "build",
#                yaml_file,
#                "--empty-workspace",
#                "--keyring-append",
#                keyring_append,
#                "--repository-append",
#                repository_append,
#                arch=arch,
#                log_policy=log_file)
#     except ErrorReturnCode_1 as e:
#         raise MelangeBuildError(str(e.stderr)) from e


def _insert_arg_name(arg_name: str, vals: List[str]) -> List[str]:
    out = []
    for v in vals:
        out += [arg_name, v]
    return out


def _melange_build(yaml_file: str,
                   out_dir: str,
                   log_file: str,
                   signing_key: str=None,
                   keyring_list: List[str]=None,
                   repository_list: List[str]=None,
                   arch_list: List[str]=None):
    list_cmds = _insert_arg_name("-k", keyring_list) \
                + _insert_arg_name("-r", repository_list) \
                + _insert_arg_name("--arch", arch_list)
    if list_cmds == []:
        try:
            melange("build", yaml_file,
                    out_dir=out_dir,
                    log_policy=log_file,
                    signing_key=signing_key)
        except ErrorReturnCode_1 as e:
            raise MelangeBuildError(str(e.stderr)) from e
    else:
        try:
            melange("build", yaml_file,
                    *list_cmds,
                    out_dir=out_dir,
                    log_policy=log_file,
                    signing_key=signing_key)
        except ErrorReturnCode_1 as e:
            raise MelangeBuildError(str(e.stderr)) from e


def melange_build(yaml_file: str,
                  out_dir: str,
                  log_file: str,
                  signing_key: str=None,
                  keyring_list: List[str]=None,
                  repository_list: List[str]=None,
                  arch_list: List[str]=None) -> str:
    """
    Builds a package for the given melange file.

    IMPORTANT: All provided file paths must be relative

    @param yaml_file: The melange yaml file
    @param log_file: The name of the log file for the build
    @param keyring_append: Keyrings for the build. Passed to --keyring-append.
    @param repository_append: Repositories for the build. Passed to --keyring-append.
    @param arch: Architectures to build
    @returns The directory containing the builds
    @raises `MelangeBuildError` if an error occurred during the build
    """

    _melange_build(yaml_file,
                   out_dir=out_dir,
                   log_file=log_file,
                   signing_key=signing_key,
                   keyring_list=keyring_list,
                   repository_list=repository_list,
                   arch_list=arch_list)

    return "packages"


def melange_build_wolfi(package: str,
                        workspace: str,
                        keys_dir: str,
                        arch: List[str] | str=None) -> str:
    """
    Builds a package for the given melange file with the Wolfi keyring and
    repository appended.

    IMPORTANT: All provided file paths must be relative

    @param yaml_file: The melange yaml file.
    @param log_file: The name of the log file for the build
    @param keyring_append: Keyrings for the build. Passed to --keyring-append.
    @param repository_append: Repositories for the build. Passed to --keyring-append.
    @param arch: Architectures to build
    @returns The directory containing the builds
    @raises `MelangeBuildError` if an error occurred during the build
    """
    yaml_file = os.path.join(workspace, f"{package}.yaml")

    out_dir = os.path.join(workspace, "packages")
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)

    log_file = os.path.join(workspace, f"{package}.log")
    signing_key = os.path.join(keys_dir, "melange.rsa")
    local_keyring = os.path.join(keys_dir, "melange.rsa.pub")

    return melange_build(yaml_file,
                         out_dir,
                         log_file=log_file,
                         signing_key=signing_key,
                         keyring_list=[WOLFI_KEYRING, local_keyring],
                         repository_list=[WOLFI_REPOSITORY],
                         arch_list=[arch])

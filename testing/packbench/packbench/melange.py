from typing import List
from sh import melange, ErrorReturnCode_1


WOLFI_KEYRING = "https://packages.wolfi.dev/os/wolfi-signing.rsa.pub"
WOLFI_REPOSITORY = "https://packages.wolfi.dev/os"


def _arg_to_strings(arg: str | List[str]=None) -> str:
    """
    Parses a `str` or `List[str]` into a strings argument.
    For example:

    arg="arg1" => "arg1"
    arg=["arg1", "arg2"] => "arg1 arg2"
    """
    if arg is None:
        return None

    if isinstance(arg, str):
        return arg

    if isinstance(arg, list):
        return " ".join(arg)

    return _arg_to_strings(str(arg))


def _append_arg(val: str, arg: str | List[str]=None) -> str | List[str]:
    """
    Appends a value to an argument and returns the result converted
    into a strings argument.
    """
    if arg is None:
        return val

    if isinstance(arg, str):
        return _arg_to_strings([arg, val])

    if isinstance(arg, list):
        return _arg_to_strings(arg.append(val))

    new_arg = _append_arg(val, str(arg))
    return _arg_to_strings(new_arg)


def melange_build(yaml_file: str,
                  out_dir="packages",
                  log_file: str="build.log",
                  keyring_append: List[str] | str=None,
                  repository_append: List[str] | str=None,
                  arch: List[str] | str=None):
    
    key_strings = _arg_to_strings(keyring_append)
    repo_strings = _arg_to_strings(repository_append)
    arch_strings = _arg_to_strings(arch)

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

    keys = _append_arg(WOLFI_KEYRING, keyring_append)
    repos = _append_arg(WOLFI_REPOSITORY, repository_append)
    
    return melange_build(yaml_file,
                         out_dir=out_dir,
                         log_file=log_file,
                         keyring_append=keys,
                         repository_append=repos,
                         arch=arch)

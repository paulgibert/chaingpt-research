import logging
from .tools import run_sh, list_dir


def system_run_sh(command: str) -> str:
    """
    Run a shell command in the current working directory. Shell
    commands should be safe and not harmful to the system. All commands
    must be approved by the user. If the user rejects a command, an error
    is returned. The contents of stdout and stderr are written to a file
    which can be examined for helpful logs and errors. The name of this file
    is returned. Note that all commands are run independently in subshells.
    Therefore, any environmental variables you create will not peresist in the
    next call to run_sh. Chain your shell commands using &&, |, >, ect accordingly.
    """
    logging.info(f"Executing: {command}")
    return run_sh(command)


def system_list_dir(path: str) -> str:
    """
    Returns a list of the contents of the directory at the provided path.
    Useful for exploring a GitHub repo to determine what files need to be read.
    If the provided path is not found, an error is returned.
    """
    logging.info(f"Listing directory contents of {path}")
    try:
        return list_dir(path)
    except FileNotFoundError:
        logging.error(f"Path not found. {path} does not exist.")
        return "Error: Path not found"

import os
import subprocess
from typing import List
from langchain.tools import BaseTool, StructuredTool
from langchain.agents.agent_toolkits.base import BaseToolkit
from .exceptions import PathNotFoundError


def run_sh(command: str) -> str:
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
    response = input(f"Allow \'{command}\' (y/N)? ")
    if response == "y":
        with open("cmd_out.txt", "w") as f:
            subprocess.run(command, stdout=f, stderr=f, text=True, shell=True)
        return "cmd_out.txt"
    else:
        return "Error: The user rejected the command."


def list_dir(path: str) -> str:
    """
    Returns a list of the contents of the directory at the provided path.
    Useful for exploring a GitHub repo to determine what files need to be read.
    If the provided path is not found, an error is returned.
    """
    contents = os.listdir(path) #TODO: Dangerous
    dirs = next(os.walk(path))[1]
    try:
        contents = os.listdir(path)
    except FileNotFoundError:
        return "Error: " + str(PathNotFoundError())
    
    results = ""
    for c in contents:
        if c in dirs:
            results += c + "(dir)\n"
        else:
            results += c + "\n"
    return results
import os
import subprocess
from langchain.tools import tool
from utils import log_tool


@tool
def run_sh_command(command: str) -> str:
    """
    Run a shell command in the current working directory. Shell
    commands should be safe and not harmful to the system. The
    contents of stdout and stderr are returned. Useful
    for testing build commands and receiving feedback.
    """
    log_tool("run_sh_command", command, end="")
    permission = input(" Allow? (y/N): ")
    if permission == "y":
        try:
            result = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
            return result[-1000:]
        except subprocess.CalledProcessError as e:
            return e.output[-1000:]
    else:
        return "User did not allow command to run."


@tool
def git_clone(repository: str, branch: str=None, tag: str=None) -> str:
    """
    Clones a git repository and returns the name of the top level directory
    which may be used for constructing paths to files within the repository.
    """
    log_tool("git_clone", repository)
    cmd = "git clone"
    if branch:
        cmd += " -b " + branch
    elif tag:
        cmd += " -b " + tag
    cmd += " " + repository
    os.system(cmd)
    repo_name = repository.split("/")[-1]
    repo_name = repo_name.split(".")[0]
    return repo_name


@tool
def git_list_dir(path: str) -> str:
    """
    Returns a list of the contents of the directory provided from the clone GitHub repo.
    Useful for exploring a GitHub repo to determine what files need to be read.
    """
    log_tool("git_list_dir", path)
    contents = os.listdir(path) #TODO: Dangerous
    return "\n".join(contents)


@tool
def git_read_file(path: str) -> str:
    """
    Returns the content of a file at the specified path
    """
    log_tool("git_read_file", path)
    try:
        with open(path, "r", encoding="utf-8") as f: #TODO: Dangerous
            text = f.read()[:3000]
    except FileNotFoundError:
        return "That file does not exist."
    return text


@tool
def write_file(path:str, content: str) -> str:
    """
    Creates and writes the provided content to a file located
    at the provided path.
    """
    log_tool("write_file", path)
    if os.path.isfile(path):
        path += "_dup"
    
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
        
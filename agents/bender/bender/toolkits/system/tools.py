import os
import subprocess


def run_sh(command: str) -> str:
    """
    Runs a shell command and saves the result in cmd_out.txt.
    This is a dangerous command.
    """
    with open("cmd_out.txt", "w", encoding="utf-8") as f:
        subprocess.run(command, stdout=f, stderr=f, text=True, shell=True) # TODO: shell=True is dangerous
    return "cmd_out.txt"


def list_dir(path: str) -> str:
    """
    List the contents of a directory
    """
    contents = os.listdir(path) #TODO: Dangerous: path traversal
    dirs = next(os.walk(path))[1]
    contents = os.listdir(path)
    results = ""
    for c in contents:
        if c in dirs:
            results += c + "(dir)\n"
        else:
            results += c + "\n"
    return results

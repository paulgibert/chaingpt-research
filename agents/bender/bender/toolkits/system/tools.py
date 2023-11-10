import os
import subprocess


def run_sh(command: str) -> str:
    with open("cmd_out.txt", "w") as f:
        subprocess.run(command, stdout=f, stderr=f, text=True, shell=True)
    return "cmd_out.txt"


def list_dir(path: str) -> str:
    contents = os.listdir(path) #TODO: Dangerous
    dirs = next(os.walk(path))[1]
    contents = os.listdir(path)
    results = ""
    for c in contents:
        if c in dirs:
            results += c + "(dir)\n"
        else:
            results += c + "\n"
    return results

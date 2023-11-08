from typing import Dict, List, Tuple
import os
import yaml


MELANGE_URL = "https://github.com/chainguard-dev/melange.git"
MELANGE_PIPELINES_PATH = "pkg/build/pipelines"


def _git_clone(url: str) -> str:
    os.system(f"git clone {url}")
    repo_name = url.split("/")[-1].split(".")[0]
    return repo_name


def pipeline_params(pipeline: Dict) -> Tuple[List[str], List[str]]:
    try:
        packages = pipeline["needs"]["packages"]
    except KeyError:
        packages = []
    inputs = []
    if "inputs" in pipeline.keys():
        for k, v in pipeline["inputs"].items():
            desc = v["description"].replace("\n", "")
            s = f"{k}: {desc}"
            if "default" in v.keys():
                default = "\"" + str(v["default"]) + "\""
                s += f" (default: {default})"
            if "required" in v.keys():
                if v["required"]:
                    s += " (required)"
            inputs.append(s)
    return packages, inputs


def pipeline_str(name: str, pipeline: Dict) -> str:
    packages, inputs = pipeline_params(pipeline)
    s = name + ":\n\tpackages:"
    for p in packages:
        s += "\n\t\t" + p
    s += "\n\tinputs:"
    for i in inputs:
        s += "\n\t\t" + i
    return s + "\n"


def get_pipelines():
    repo_name = _git_clone(MELANGE_URL)
    pipelines_path = os.path.join(repo_name, MELANGE_PIPELINES_PATH)
    for dirname, _, files in os.walk(pipelines_path):
        for fname in files:
            if ".yaml" not in fname:
                continue
            with open(os.path.join(dirname, fname), "r") as f:
                pipeline = yaml.safe_load(f)
                basename = os.path.basename(dirname)
                name = ""
                if basename != "pipelines":
                    name += basename + "/"
                name += fname.split(".")[0]
                print(pipeline_str(name, pipeline))
    os.system(f"rm -rf {repo_name}") #TODO: Dangerous



if __name__ == "__main__":
    get_pipelines()

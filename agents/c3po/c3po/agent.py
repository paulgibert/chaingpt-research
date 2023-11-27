from typing import Dict
import os
import shutil
import logging
import re
import argparse
import json
import yaml
from yaspin import yaspin
from yaspin.spinners import Spinners
from colorama import Fore
from c3po.repo_setup import init_repository
from c3po.store_setup import common_doc_files
from c3po.assistant import run_assistant
from c3po.melange import create_melange_yaml


def _init_workspace(workspace):
    if os.path.exists(workspace):
        shutil.rmtree(workspace)
    os.mkdir(workspace)
    os.chdir(workspace)


def _cleanup_workspace(workspace):
    os.chdir("..")
    shutil.rmtree(workspace)


def _parse_json_from_output_str(output_str) -> Dict:
    match = re.search("```json\s(.*?)\s```", output_str, re.DOTALL)
    if match is not None:
        json_str = match.group(0)[8:-4]
        return json.loads(json_str)
    return None


def _validate_json_output(data: Dict):
    required = ["description", "license", "steps"]
    for field in required:
        if field not in data.keys():
            msg = f"JSON output is missing `{field}` field"
            logging.info(msg)
            print(Fore.RED + msg)
            raise ValueError(msg)


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("package",
                        help="The name of the package")
    parser.add_argument("version",
                        help="The version of the package")
    parser.add_argument("--repository",
                        help="Force the agent to use a GitHub repository")
    parser.add_argument("--workspace",
                        default=".agent-workspace",
                        help="The name of the tmp directory used as a workspace")
    parser.add_argument("--output-yaml",
                        default="out.yaml",
                        help="The location to save the generated YAML")
    parser.add_argument("--output-log",
                        default="agent.log",
                        help="The location to save the log file")
    return parser.parse_args()



def run_agent():
    # Parse args
    args = _parse_args()

    # Setup logging
    logging.basicConfig(filename=args.output_log, encoding='utf-8', level=logging.INFO)

    # Create and cd into a workspace to store artifacts such as the cloned repo
    print(Fore.BLUE + f"Creating workspace {args.workspace}")
    _init_workspace(args.workspace)

    # Search for a clone the repository into the local workspace
    repo = init_repository(args.package, args.version)
    if repo is None:
        return

    # Identify documentation
    with yaspin(Spinners.line, text=Fore.BLUE + "Scanning repository for documentation", color="blue"):
        doc_file_paths = common_doc_files(repo)

    # Run OpenAI assistant to generate YAML from documentation
    output = run_assistant(args.package, args.version, repo, doc_file_paths)

    # Parse and validate JSON from the assistant output
    print(Fore.BLUE + "Parsing assistant response")
    data = _parse_json_from_output_str(output)
    try:
        _validate_json_output(data)
    except ValueError:
        data = None

    if data is None:
        print(Fore.RED + "Failed :(")
        print(Fore.RED + output)
        return

    print(Fore.GREEN + "Success :)")

    # Format the JSON assistant output as a melange YAML
    yaml_data = create_melange_yaml(args.package, args.version,
                                    description=data["description"],
                                    license=data["license"],
                                    build_steps=data["steps"])

    # Cleanup the workspace first to restore the original working directory of the program
    # before saving the generated YAML file
    print(Fore.BLUE + "Removing workspace")
    _cleanup_workspace(args.workspace)

    # Save the YAML
    with open(args.output_yaml, "w", encoding="utf-8") as f:
        yaml.safe_dump(yaml_data, f, sort_keys=False, indent=2)

    print(Fore.GREEN + f"YAML saved to {args.output_yaml}")


if __name__ == "__main__":
    run_agent()

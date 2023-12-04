from typing import Dict
import os
import shutil
import logging
import re
import json
import yaml
from yaspin import yaspin
from yaspin.spinners import Spinners
from colorama import Fore
from c3po.repo_setup import init_repository
from c3po.store_setup import common_doc_files
from c3po.assistant import run_assistant
from c3po.melange import create_melange_yaml


def _print_banner():
    banner = """
██████╗██╗  ██╗ █████╗ ██╗███╗   ██╗ ██████╗ ██████╗ ████████╗
██╔════╝██║  ██║██╔══██╗██║████╗  ██║██╔════╝ ██╔══██╗╚══██╔══╝
██║     ███████║███████║██║██╔██╗ ██║██║  ███╗██████╔╝   ██║   
██║     ██╔══██║██╔══██║██║██║╚██╗██║██║   ██║██╔═══╝    ██║   
╚██████╗██║  ██║██║  ██║██║██║ ╚████║╚██████╔╝██║        ██║   
 ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚═╝        ╚═╝   

 
               ( )
     __       //|\\\\
    /_0\      \\\\_//
   [|o=|]      |||
___/|--|\______|||________C3PO

"""
    print(banner)


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
    required = ["summary", "description", "license", "steps"]
    for field in required:
        if field not in data.keys():
            msg = f"JSON output is missing `{field}` field"
            logging.info(msg)
            print(Fore.RED + msg)
            raise ValueError(msg)


def run_agent(package: str, version: str,
              output_yaml: str,
              repository: str=None,
              workspace: str=".agent-workspace",
              output_log: str="c3po.log",
              output_summary: str=None):
    # Parse args
    # args = _parse_args()
    _print_banner()

    # Setup logging
    logging.basicConfig(filename=output_log, encoding='utf-8', level=logging.INFO, force=True)

    print(Fore.BLUE + f"Generating Melange YAML for {package} {version}")

    # Create and cd into a workspace to store artifacts such as the cloned repo
    print(Fore.BLUE + f"Creating workspace {workspace}")
    _init_workspace(workspace)

    # Search for a clone the repository into the local workspace
    repo = init_repository(package, version)
    if repo is None:
        _cleanup_workspace(workspace)
        return

    # Identify documentation
    print(Fore.BLUE + "Scanning repository for documentation")
    doc_file_paths = common_doc_files(repo)

    # Run OpenAI assistant to generate YAML from documentation
    output = run_assistant(package, version, repo, doc_file_paths)

    # Parse and validate JSON from the assistant output
    print(Fore.BLUE + "Parsing assistant response")
    data = _parse_json_from_output_str(output)
    if data is not None:
        try:
            _validate_json_output(data)
        except ValueError:
            data = None

    if data is None:
        print(Fore.RED + "Failed :(")
        print(Fore.RED + output)
        logging.info("Failed: %s", output)
        _cleanup_workspace(workspace)
        return

    print(Fore.GREEN + "Success :)")

    # Format the JSON assistant output as a melange YAML
    yaml_data = create_melange_yaml(package, version,
                                    description=data["description"],
                                    license=data["license"],
                                    build_steps=data["steps"])

    # Cleanup the workspace first to restore the original working directory of the program
    # before saving the generated YAML file
    print(Fore.BLUE + "Removing workspace")
    _cleanup_workspace(workspace)

    # Save the YAML
    with open(output_yaml, "w", encoding="utf-8") as f:
        yaml.safe_dump(yaml_data, f, sort_keys=False, indent=2)
    print(Fore.GREEN + f"YAML saved to {output_yaml}")

    # Save the summary
    if output_summary is not None:
        with open(output_summary, "w", encoding="utf-8") as f:
            f.write(data["summary"])
        print(Fore.GREEN + f"Summary saved to {output_summary}")

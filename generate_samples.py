from typing import Tuple
import os
import shutil
import subprocess
import argparse
import yaml


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent",
                        choices=["ava", "bender", "c3po"],
                        default="c3po",
                        help="The agent to generate YAMLs with")
    parser.add_argument("--samples-dir",
                        default="samples",
                        help="The directory containing the ORIGINAL YAML samples")
    parser.add_argument("--output-dir",
                        default="generated",
                        help="The directory to write generated YAMLs to. Does not have to exist")
    return parser.parse_args()


def package_version(yaml_path: str) -> Tuple[str, str]:
    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        try:
            return data["package"]["name"], data["package"]["version"]
        except KeyError as e:
            print(f"Error reading package name and version from {yaml_path}: {str(e)}")


def run_c3po(package: str, version: str, output_yaml: str):
    docker_cmd = "docker run -it --rm -v ./work c3po-agent"
    python_cmd = f"python c3po/agent.py --output-yaml {output_yaml} {package} {version}"
    # subprocess.run(docker_cmd, shell=True)
    subprocess.run(docker_cmd + " " + python_cmd, shell=True)


def main():
    args = parse_args()

    if os.path.exists(args.output_dir):
        shutil.rmtree(args.output_dir)
    os.mkdir(args.output_dir)

    for filename in os.listdir(args.samples_dir):
        sample_path = os.path.join("samples", filename)
        package, version = package_version(sample_path)
        out_path = os.path.join(args.output_dir, f"{package}.yaml")
        # TODO: Currently only supports c3po
        run_c3po(package, version, out_path)


if __name__ == "__main__":
    main()

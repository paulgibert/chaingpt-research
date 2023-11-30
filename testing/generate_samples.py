from typing import Iterator, Tuple
import os
import shutil
import argparse
import yaml
from c3po import run_agent


def package_iter(samples_dir: str) -> Iterator[Tuple[str, str]]:
    original_dir = os.path.join(samples_dir, "original")
    for package in os.listdir(original_dir):
        yaml_file = os.path.join(original_dir, package, f"{package}.yaml")
        with open(yaml_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            name = data["package"]["name"]
            version = data["package"]["version"]
            yield name, version


def gen_with_c3po(package: str, version: str, yaml_out: str, log_file: str, summary_out: str):
    run_agent(package, version, output_yaml=yaml_out, output_log=log_file,
              output_summary=summary_out)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", default=3,
                        type=int,
                        help="Number of runs per package")
    return parser.parse_args()


def main():
    args = parse_args()

    gen_path = os.path.join("samples", "generated")
    if not os.path.exists(gen_path):
        os.mkdir(gen_path)

    for package, version in package_iter("samples"):
        for i in range(args.n):
            out_file_dir = os.path.join("samples", "generated", f"{package}_{i}")
            if os.path.exists(out_file_dir):
                shutil.rmtree(out_file_dir)
            os.mkdir(out_file_dir)

            yaml_out_file = os.path.join(out_file_dir, f"{package}.yaml")
            log_file = os.path.join(out_file_dir, f"c3po-{package}.log")
            summary_out_file = os.path.join(out_file_dir, f"{package}-build-summary.txt")
            gen_with_c3po(package, version, yaml_out_file, log_file, summary_out_file)


if __name__ == "__main__":
    main()

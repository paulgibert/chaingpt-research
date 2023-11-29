"""
samples/
    original/
    generated/
        package/
            package.yaml
            package.test

logs/
    package-build.log
"""
from typing import Iterator, Tuple
import os
import shutil
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


def gen_with_c3po(package: str, version: str, out_file: str, log_file: str):
    # #  cmd = f"python c3po/c3po/main.py {package} {version} --output-yaml {out_file} --output-log {log_file}"
    # cmd = "sh"
    # print(docker("run", "--rm", "-it",
    #        "-v", "./:/work",
    #        "c3po-agent:latest",
    #        cmd,
    #        _tty_in=True))
    run_agent(package, version, output_yaml=out_file, output_log=log_file)


def main():
    gen_path = os.path.join("samples", "generated")
    if not os.path.exists(gen_path):
        os.mkdir(gen_path)

    for package, version in package_iter("samples"):
        out_file_dir = os.path.join("samples", "generated", package)
        if os.path.exists(out_file_dir):
            shutil.rmtree(out_file_dir)
        os.mkdir(out_file_dir)

        out_file = os.path.join(out_file_dir, f"{package}.yaml")
        log_file = os.path.join(out_file_dir, f"c3po-{package}.log")
        gen_with_c3po(package, version, out_file, log_file)


if __name__ == "__main__":
    main()

from typing import Tuple
import os
import subprocess
import shutil
import yaml


BUILD_ENVS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "build_env")
UTILS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "utils")
BUILD_SCRIPT_PATH = os.path.join(UTILS_PATH, "build.sh")
BUILD_TEST_SCRIPT_PATH = os.path.join(UTILS_PATH, "build_test.sh")
RUN_TEST_SCRIPT_PATH = os.path.join(UTILS_PATH, "run_test.sh")
APKO_TEMPLATE_PATH = os.path.join(UTILS_PATH, "apko_template.yaml")


def init_build_envs_dir():
    if os.path.exists(BUILD_ENVS_DIR):
        shutil.rmtree(BUILD_ENVS_DIR)
    os.mkdir(BUILD_ENVS_DIR)


def generate_keys(env_path: str) -> str:
    keys_dir = os.path.join(env_path, "keys")
    os.mkdir(keys_dir)
    cmd = f"docker run --rm -v {keys_dir}:/work cgr.dev/chainguard/melange keygen"
    subprocess.run(cmd, shell=True)
    return keys_dir


def init_build_env(package_name: str) -> str:
    if not os.path.exists(BUILD_ENVS_DIR):
        init_build_envs_dir()
    env_path = os.path.join(BUILD_ENVS_DIR, package_name)
    if os.path.exists(env_path):
        shutil.rmtree(env_path)
    os.mkdir(env_path)
    generate_keys(env_path)
    return env_path


def get_package_name(yaml_path: str):
    return os.path.basename(yaml_path).split(".")[0]


def run_build_script(yaml_path: str, env_path: str):
    subprocess.run([BUILD_SCRIPT_PATH, yaml_path, env_path])


def run_test_scripts(env_path: str, cmd: str) -> Tuple[str, str]:
    subprocess.run([BUILD_TEST_SCRIPT_PATH, env_path])
    r = subprocess.run([RUN_TEST_SCRIPT_PATH, env_path, cmd],
                       capture_output=True)
    return r.stdout, r.stderr


def make_apko_yaml(package_name: str, env_path: str):
    with open(APKO_TEMPLATE_PATH, "r", encoding="utf-8") as f_in:
        data = yaml.safe_load(f_in)
        data["contents"]["packages"].append(f"{package_name}@local")
        out_path = os.path.join(env_path, "apko.yaml")
        with open(out_path, "w", encoding="utf-8") as f_out:
            yaml.safe_dump(data, f_out, sort_keys=False)


def build_yaml(yaml_path: str, cmd: str) -> str:
    if not os.path.exists(yaml_path):
        print("Failed to load {yaml_path}.")
        return
    package = get_package_name(yaml_path)
    env_path = init_build_env(package)
    run_build_script(yaml_path, env_path)
    make_apko_yaml(package, env_path)
    return run_test_scripts(env_path, cmd)


out, err = build_yaml("grype.yaml", "grype")
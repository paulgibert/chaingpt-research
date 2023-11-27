from typing import Tuple
import os
import subprocess
import shutil
import yaml


BUILD_ENVS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
UTILS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "utils")
BUILD_SCRIPT_PATH = os.path.join(UTILS_PATH, "build.sh")
BUILD_TEST_SCRIPT_PATH = os.path.join(UTILS_PATH, "build_test.sh")
RUN_TEST_SCRIPT_PATH = os.path.join(UTILS_PATH, "run_test.sh")
APKO_TEMPLATE_PATH = os.path.join(UTILS_PATH, "apko_template.yaml")


def init_build_envs_dir():
    if os.path.exists(BUILD_ENVS_DIR):
        shutil.rmtree(BUILD_ENVS_DIR)
    os.mkdir(BUILD_ENVS_DIR)


def _generate_keys(env_path: str) -> str:
    """
    Generates signing keys
    """
    keys_dir = os.path.join(env_path, "keys")
    os.mkdir(keys_dir)
    cmd = f"docker run --rm -v {keys_dir}:/work cgr.dev/chainguard/melange keygen"
    subprocess.run(cmd, shell=True)
    return keys_dir


def _init_build_env(package_name: str) -> str:
    """
    Creates a directory to house build artifacts
    """
    if not os.path.exists(BUILD_ENVS_DIR):
        init_build_envs_dir()
    env_path = os.path.join(BUILD_ENVS_DIR, package_name)
    if os.path.exists(env_path):
        shutil.rmtree(env_path)
    os.mkdir(env_path)
    return env_path


def get_package_name_and_version(yaml_path: str):
    """
    Returns the name of a package from the provided melange YAML
    """
    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        name = data["package"]["name"]
        version = data["package"]["version"]
        return name, version


def _build(yaml_dir: str, yaml_fname: str, env_path: str):
    """
    Calls a build script to build the package
    from the melange YAML.
    """
    subprocess.run([BUILD_SCRIPT_PATH, yaml_dir, yaml_fname, env_path])


def _setup_apko(package_name: str, env_path: str):
    """
    Creates an apko YAML for testing
    """
    with open(APKO_TEMPLATE_PATH, "r", encoding="utf-8") as f_in:
        data = yaml.safe_load(f_in)
        data["contents"]["packages"].append(f"{package_name}@local")
        out_path = os.path.join(env_path, "apko.yaml")
        with open(out_path, "w", encoding="utf-8") as f_out:
            yaml.safe_dump(data, f_out, sort_keys=False)


def build_yaml(yaml_path) -> Tuple[str, str]:
    if not os.path.exists(yaml_path):
        raise FileNotFoundError(f"Failed to find {yaml_path}")
    package, _ = get_package_name_and_version(yaml_path)
    env_path = _init_build_env(package)
    _generate_keys(env_path)
    yaml_dir = os.path.dirname(yaml_path)
    yaml_fname = os.path.basename(yaml_path)
    _build(yaml_dir, yaml_fname, env_path)
    return env_path, f"{package}.yaml"


def try_command(env_path: str, command: str) -> Tuple[str, str]:
    """
    After the melange YAML has been built and apko has been setup,
    this method is called to spawn a docker container
    and test a command. Returns a `Tuple` (stdout, stderr)
    """
    subprocess.run([BUILD_TEST_SCRIPT_PATH, env_path])
    r = subprocess.run([RUN_TEST_SCRIPT_PATH, env_path, command],
                       capture_output=True)
    return r.stdout, r.stderr


# def build_and_test_yaml(yaml_path: str, command: str) -> str:
#     """
#     Builds a melange YAML and installs the package
#     in a docker container. The provided command is
#     run in this container and the output is returned.

#     @param yaml_path: The path to the melange YAML
#     @param command: The command to run in teh container
#     @returns The command output
#     @raises `FileNotFoundError` if the provided yaml file does not exist
#     """
#     if not os.path.exists(yaml_path):
#         raise FileNotFoundError(f"Failed to find {yaml_path}")
#     package = _get_package_name(yaml_path)
#     env_path = _init_build_env(package)
#     _generate_keys(env_path)
#     _build(yaml_path, env_path)
#     _setup_apko(package, env_path)
#     return _test_command(env_path, command)

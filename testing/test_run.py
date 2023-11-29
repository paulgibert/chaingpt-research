from typing import Iterator, Tuple
import os
import pytest
from packbench.apko import apko_build_wolfi_test_image
from sh import docker


def _get_test_commands(samples_dir: str) -> Iterator[Tuple[str, str, str]]:
    org_dir = os.path.join(samples_dir, "original")
    gen_dir = os.path.join(samples_dir, "generated")
    for package in os.listdir(org_dir):
        test_file = os.path.join(org_dir, package, f"{package}.test")
        if os.path.exists(os.path.join(gen_dir, package, f"{package}.yaml")):
            with open(test_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                test_command = lines[0]
                expected_output = lines[1]
                yield package, test_command, expected_output


def _create_image(archive: str):
    with open(archive, "rb") as f:
        docker("load", _in=f)


def _run_command_in_image(image: str, command: str):
    command_args = command.split(" ")
    output = docker("run", "--rm", "-it",
               image, *command_args, _tty_in=True)
    return output.strip("^@\r\n")


def _rm_image(image: str):
    docker("image", "rm", image)


@pytest.mark.parametrize("package, test_command, expected_output", _get_test_commands("samples"))
def test_package_runs(package: str, test_command: str, expected_output: str):
    workspace_dir = os.path.join("samples", "generated", package)
    keys_dir = "keys"
    archive = apko_build_wolfi_test_image(package, workspace_dir, keys_dir, "x86_64")
    image = f"apko-{package}:test-amd64"
    _create_image(archive)
    output = _run_command_in_image(image, test_command.strip("\n"))
    _rm_image(image)
    assert output == expected_output

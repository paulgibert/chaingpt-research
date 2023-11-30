from typing import Iterator, Tuple
import os
import yaml
import pytest
from packbench.melange import melange_build_wolfi


# SAMPLES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "samples")
SAMPLES_DIR = "samples"
KEYS_DIR = "keys"


def _get_workspaces(samples_dir: str) -> Iterator[Tuple[str, str]]:
    gen_dir = os.path.join(samples_dir, "generated")
    for package_dir in os.listdir(gen_dir):
        package = package_dir.split("_")[0]
        yield package, os.path.join(gen_dir, package_dir)


@pytest.mark.parametrize("package, workspace_dir", _get_workspaces(SAMPLES_DIR))
def test_package_builds(package: str, workspace_dir: str):
    packages_dir = melange_build_wolfi(package, workspace_dir, KEYS_DIR, arch="x86_64")
    assert packages_dir == "packages"

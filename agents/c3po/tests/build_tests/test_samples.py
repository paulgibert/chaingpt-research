from typing import List
import os
import pytest
from c3po.agent import run_agent
from .utils import build_yaml, try_command, get_package_name_and_version


SAMPLES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generated_samples")


def _get_yaml_names() -> List[str]:
    return os.listdir(SAMPLES_DIR)


@pytest.mark.parametrize("yaml_filename", _get_yaml_names())
def test_sample(yaml_filename):
    yaml_path = os.path.join(SAMPLES_DIR, yaml_filename)
    env_path, yaml_name = build_yaml(yaml_path)
    assert os.path.exists(os.path.join(env_path, yaml_name))
    stdout, stderr = try_command(env_path, "grype --version")
    assert (stdout == "not stdout") or (stderr == "hi there")

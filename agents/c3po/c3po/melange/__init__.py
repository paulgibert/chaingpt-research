from typing import List
import os
import yaml
from .exceptions import BuildStepYamlParseError
from .model import create_melange_yaml


BUILD_STEPS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "build_steps")


def _build_step_to_prompt(yaml_str: str) -> str:
    """
    Creates a `str` prompt for the build step
    described in the provided YAML file.
    """
    data = yaml.safe_load(yaml_str)
    keys = list(data.keys())
    if len(keys) == 0:
        raise BuildStepYamlParseError("Cannot parse an empty YAML")
 
    type = keys[0]
    if "description" not in data[type].keys():
        raise BuildStepYamlParseError("Build step YAMLs must have a `description` field")

    prompt = f"Step type: {type} - {data[type]['description']}"

    prompt += "\nFields:"
    fields = data[type].get("fields", {})
    for name, details in fields.items():
        if "description" not in details.keys():
            raise ValueError("Build step YAMLs must have a `description` for each field.")
        required = 'required' if details.get('required', False) else 'optional'
        prompt += f"\n'{name}' ({required}) - {details['description']}"
    return prompt


def get_build_step_prompts() -> List[str]:
    """
    Creates `str` descriptions for each build step
    described in melange/build_steps/

    @returns A `List` of prompts
    @raises BuildStepYamlParseError if a build step YAML is not properly formatted
    """
    filenames = os.listdir(BUILD_STEPS_DIR)
    prompts = []
    for fname in filenames:
        path = os.path.join(BUILD_STEPS_DIR, fname)
        with open(path, "r", encoding="utf-8") as f:
            yaml_str = f.read()
            prompts.append(_build_step_to_prompt(yaml_str))
    return prompts

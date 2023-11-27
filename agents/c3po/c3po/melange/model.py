from typing import List, Dict


def _step_to_stage(stage: Dict) -> Dict:
    if stage["type"] == "shell":
        return {"runs": stage["command"]}

    result = {"uses": stage["type"]}
    result["with"] = {}
    for key, value in stage.items():
        if key == "type":
            continue
        result["with"][key] = value
    return result


def create_melange_yaml(package: str, version: str,
                        description: str, license: str,
                        build_deps: List[str]=None,
                        build_steps: List[Dict]=None) -> Dict:
    return {
        "package": {
            "name": package,
            "version": version,
            "description": description,
            "copyright": [{"license": license}]
        },
        "environment": {
            "contents": {
                "packages": ["wolfi-base", "build-base"] # TODO Implement build dependencies
            }
        },
        "pipeline": [_step_to_stage(s) for s in build_steps],
    }

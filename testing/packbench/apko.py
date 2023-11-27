import os
import yaml
from sh import apko, docker


WOLFI_TEMPLATE_YAML = os.path.join(os.path.dirname(os.path.abspath(__file__)), "apko-wolf.yaml")


def apko_build_image(yaml_file: str, image_name: str, image_tag: str) -> str:
    archive = f"{image_name}.tar.gz"
    apko("build", yaml_file,
         f"{image_name}:{image_tag}",
         archive)
    return archive


def create_apko_yaml_from_template(template_file: str, package_name: str) -> str:
    with open(template_file, "r", encoding="utf-8") as f_template:
        data = yaml.safe_load(f_template)

        if "contents" not in data.keys():
            raise ValueError("Template file must have a `contents` section")

        if "packages" not in data["contents"].keys():
            raise ValueError("Template file must have a `packages` section under `contents`")

        data["contents"]["packages"].append(f"{package_name}@local")

        out_path = f"apko-wolfi-{package_name}.yaml"
        with open(out_path, "w", encoding="utf-8") as f_out:
            yaml.safe_dump(data, f_out, sort_keys=False)

        return out_path


def apko_build_wolfi_test_image(package_name: str):
    yaml_file = create_apko_yaml_from_template(WOLFI_TEMPLATE_YAML, package_name)
    archive = apko_build_image(yaml_file, package_name, "latest")
    docker("load", _in=archive)
    return f"{package_name}:latest"


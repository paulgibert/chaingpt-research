from typing import List, Tuple
import os
import yaml
from sh import apko, docker, ErrorReturnCode_1
from .exceptions import APKOBuildError


WOLFI_YAML = os.path.join(os.path.dirname(os.path.abspath(__file__)), "apko-wolfi.yaml")


# def _apko_build(yaml_file: str, image_name: str, image_tag_basname: str,
#                 archive_out_file: str, key: str, arch: str, log_file: str):
#     try:
#         docker("run", "--rm", "-v", ".:/work",
#             "-w", "/work", "cgr.dev/chainguard/apko",
#             "build", yaml_file, f"{image_name}:{image_tag_basname}",
#             archive_out_file, "-k", key, log_policy=log_file)
#     except ErrorReturnCode_1 as e:
#         raise APKOBuildError(str(e)) from e


def _apko_build(yaml_file: str, image_name:
                str, tag_basename: str, archive_out_file: str,
                key: str, arch: str, log_file: str):
    try:
        apko("build", yaml_file, f"{image_name}:{tag_basename}",
             archive_out_file, "--sbom=false",
             k=key, arch=arch,
             log_policy=log_file)
    except ErrorReturnCode_1 as e:
        raise APKOBuildError(str(e))


def apko_build_image(yaml_file: str,
                     image_name: str, tag_basename: str,
                     archive_out_file: str, key: str, arch: str, log_file: str):
    _apko_build(yaml_file, image_name, tag_basename,
                archive_out_file=archive_out_file, key=key,
                arch=arch, log_file=log_file)


def create_apko_yaml_from_template(template_file: str, package: str, packages_dir: str, out_file: str):
    with open(template_file, "r", encoding="utf-8") as f_template:
        data = yaml.safe_load(f_template)

        if "contents" not in data.keys():
            raise ValueError("Template file must have a `contents` section")

        if "packages" not in data["contents"].keys():
            raise ValueError("Template file must have a `packages` section under `contents`")

        if "repositories" not in data["contents"].keys():
            raise ValueError("Template file must have a `repositories` section under `contents`")

        data["contents"]["packages"].append(f"{package}@local")
        data["contents"]["repositories"].append(f"@local {os.path.abspath(packages_dir)}")

        with open(out_file, "w", encoding="utf-8") as f_out:
            yaml.safe_dump(data, f_out, sort_keys=False)


def apko_build_wolfi_test_image(package: str, workspace_dir: str,
                                keys_dir: str,
                                arch: str) -> str:
    image = f"apko-{package}"
    packages_dir = os.path.join(workspace_dir, "packages")
    yaml_out_file = os.path.join(workspace_dir, f"apko-{package}.yaml")
    create_apko_yaml_from_template(WOLFI_YAML, package,
                                   packages_dir=packages_dir,
                                   out_file=yaml_out_file)

    archive_out_file = os.path.join(workspace_dir, f"apko-{package}.tar")
    log_file = os.path.join(workspace_dir, f"apko-{package}.log")
    tag_basename = "test"
    key = os.path.join(keys_dir, "melange.rsa.pub")
    apko_build_image(yaml_out_file,
                     image, tag_basename=tag_basename,
                     archive_out_file=archive_out_file,
                     key=key, arch=arch, log_file=log_file)

    return os.path.join(workspace_dir, f"apko-{package}.tar")

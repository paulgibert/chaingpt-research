import os
import shutil
from c3po.agent import run_agent
from utils import get_package_name_and_version

ORIGINAL_SAMPLES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "original_samples")
GENERATED_SAMPLES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generated_samples")


def main():
    if os.path.exists(GENERATED_SAMPLES_DIR):
        r = input("Found previously generated samples. Delete y/N? ")
        if r == "y":
            shutil.rmtree(GENERATED_SAMPLES_DIR)
        else:
            return
    os.mkdir(GENERATED_SAMPLES_DIR)
    for filename in os.listdir(ORIGINAL_SAMPLES_DIR):
        org_yaml_path = os.path.join(ORIGINAL_SAMPLES_DIR, filename)
        package, version = get_package_name_and_version(org_yaml_path)
        gen_yaml_path = os.path.join(GENERATED_SAMPLES_DIR, f"{package}.yaml")
        run_agent(package, version, gen_yaml_path)


if __name__ == "__main__":
    main()

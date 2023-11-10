import os
import shutil
import argparse
import subprocess


N_RUNS_DEFAULT = 10
VERSION_PLACEHOLDER = "latest"
PROJECT_TOPLVL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../..")
BENDER_BIN_PATH = os.path.join(PROJECT_TOPLVL_DIR, "agents/bender/bender/main.py")
WORK_DIR = "tmp"
SRC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../agents/bender/bender")


class UserCancelError(Exception):
    pass
    

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("samples",
                        help="The location of sample .yaml files")
    parser.add_argument("output",
                        help="The output directory for generated .yaml files")
    parser.add_argument("-n", default=N_RUNS_DEFAULT,
                        help="The number of runs per package")
    return parser.parse_args()


def run_bender(package: str, version: str, outpath: str, out_filename: str):
    cmd = f"docker run -it --rm -v {outpath}:/output -v {SRC_DIR}:/work/bender bender-agent python bender/main.py {package} -v {version} -o {out_filename}"
    subprocess.run(cmd, shell=True)

def make_output_dir(path: str):
    if os.path.exists(path):
        r = input(f"{path} contains data from a previous experiment. Overwrite (y/N)? ")
        if r != "y":
            raise UserCancelError("User canceled experiment")
        shutil.rmtree(path)
    os.mkdir(path)


def main():
    args = parse_args()

    if not os.path.exists(args.samples):
        print("Error: Samples directory was not found")
    
    make_output_dir(args.output)
    
    for filename in os.listdir(args.samples):
        package_name = filename.split(".")[0]
        package_dir = os.path.join(os.path.abspath(args.output), package_name)
        os.mkdir(package_dir)
        
        # Copy original .yaml over
        shutil.copyfile(os.path.join(args.samples, filename), os.path.join(package_dir, "original.yaml"))

        for i in args.n:
            out_filename = f"run_{i}.yaml"
            run_bender(package_name, VERSION_PLACEHOLDER, package_dir, out_filename)


if __name__ == "__main__":
    main()
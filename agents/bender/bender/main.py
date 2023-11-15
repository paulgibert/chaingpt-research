import os
import sys
import argparse
import shutil
import logging
from agent import Agent
from toolkits import FileToolkit, GitToolkit, SystemToolkit, MelangeToolkit, WebToolkit
from utils import load_openai_api_key


# A tmp file to hold YAML result. This will be copied to the user specified location.
TMP_YAML_PATH = "tmp.yaml"

# API Key
os.environ["OPENAI_API_KEY"] = load_openai_api_key()

# Logging
LOG_PATH = "/output/bender.log"
logging.basicConfig(filename=LOG_PATH,
                    encoding='utf-8',
                    level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

# The prompt used for generating build instructions
BUILD_PROMPT = """
You are supplied with the name of a codebase and a version.
Your goal is to locate and clone the correct branch or tag of the project's github
repository and return hyper-specific instructions for how to build the project from
source for Wolfi, a minimal linux distribution.
      
Your response should include any complete and valid bash and build commands depending
on the language of the project. You are provided tools for testing these commands,
reading their output, and correcting in the event of errors. You also have tools
for reading files including code and documentation.

You should attempt to identify what languages a project uses and consider how they are
commonly build and with what tools. You should also lookout for build scripts and Makefiles
and prioritize these if they contain functionality for building the project."""

# The prompt used for converting build instructions to a melange YAML
PACKAGE_PROMPT = """
You are given a detailed description of how to build a GitHub project from source and are
tasked with constructing a Melange YAML file that packages the project for Wolfi, a minimal
linux distribution designed for containerized applications. You will not be asked to produce
any YAML. Instead you will define the components of the YAML via the functions provided.
The YAML model you must define can be initialized using melange_add_header.
Every YAML model must have a header. In addition, every model must have a pipeline.
The pipeline contains the steps for building the project. For example, if the build
process requires building a go module, you could call melange_add_pipeline_go_build.
Pipeline steps will occur in the order you define them. Pay attention to ordering to
ensure build commands execute in the correct order. You should minimize the amount of
pipeline steps. You can repeat pipeline steps or use zero instances of a step.
Don't forget to write the model out at the very end using melange_write_model.
"""


def parse_args():
    """
    Argument parsing
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("package",
                        help="The name of the package to build")
    parser.add_argument("-v", "--version",
                        help="The package version to build")
    parser.add_argument("-o", "--output",
                        help="The output .yaml file")
    return parser.parse_args()


def main():
    """
    Defines and executes two agents for Bender's two stages:
    build instruction generation and melange YAML creation. 
    """
    args = parse_args()

    # Stage 1: Build Instructions
    build_toolkits = [GitToolkit(),
                      FileToolkit(),
                      SystemToolkit(),
                      WebToolkit()]
    build_tools = [t for tk in build_toolkits for t in tk.get_tools()]
    build_agent = Agent(BUILD_PROMPT, ["package", "version"], build_tools)
    desc = build_agent.run({"package": args.package, "version": args.version},
                           verbose=False)

    logging.info(f"BUILD INSTRUCTIONS:\n{desc}")

    # Stage 2: Melange YAML generation
    package_tools = MelangeToolkit().get_tools()
    build_agent = Agent(PACKAGE_PROMPT, ["package", "version", "build_desc"], package_tools)
    build_agent.run({"package": args.package,
                     "version": args.version,
                     "build_desc": desc},
                     verbose=False)
    
    # Copy YAML file result to the user specified location
    shutil.copyfile(TMP_YAML_PATH, f"/output/{args.output}")
    os.remove(TMP_YAML_PATH)


if __name__ == "__main__":
    main()
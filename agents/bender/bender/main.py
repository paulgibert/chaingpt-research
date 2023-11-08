import os
import argparse
from agent import Agent
from toolkits import FileToolkit, GitToolkit, SystemToolkit
from utils import load_openai_api_key


os.environ["OPENAI_API_KEY"] = load_openai_api_key()


BUILD_PROMPT = """
You are supplied with the name of a codebase and a version.
Your goal is to locate and clone the correct branch or tag of the project's github
repository and return hyper-specefic instructions for how to build the project from
source for a minimal linux distribution.
      
Your response should include any complete and valid bash and build commands depending
on the language of the project. You are provided tools for testing these commands,
reading their output, and correcting in the event of errors. You also have tools
for reading files including code and documentation.

Remember to test any build steps you report to the best of your ability or report that you
are unable to test a build step. If you are unable to find information to generate the necesssary
builds steps, you may report so as opposed to guessing. You are contained within a docker container
that you have full control over. You do not need to create any virtual environments, just install the
tools you need locally. Your environment is a wolfi linux distribution based on the wolfi-base
image. Wolfi's package manager is apk."""


PACKAGE_PROMPT = """
TODO
"""


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("package",
                        help="The name of the package to build")
    parser.add_argument("-v", "--version", default="latest",
                        help="The package version to build")
    return parser.parse_args()


def main():
    args = parse_args()
    toolkits = [GitToolkit(), FileToolkit(), SystemToolkit()]
    build_tools = [t for tk in toolkits for t in tk.get_tools()]
    build_agent = Agent(BUILD_PROMPT, ["package", "version"], build_tools)
    build_agent.run({"package": args.package, "version": args.version},
                    verbose=True)


if __name__ == "__main__":
    main()
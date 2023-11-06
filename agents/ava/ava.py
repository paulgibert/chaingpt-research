import os
import re
import argparse
from langchain.agents import AgentExecutor
from tools import git_clone, git_list_dir, git_read_file, write_file, run_sh_command
from agent import get_agent


class InvalidRepositoryError(Exception):
    pass


def check_repository(url: str):
    # Assert repo is properly formatted
    match = re.match(r"^https://github.com/(.+/)+.+$", url)
    if match is None:
        raise InvalidRepositoryError("The provided repository is not properly formatted")
    

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--repository",
                        required=True,
                        help="The repository to analyze")
    args = parser.parse_args()
    repo = args.repository

    check_repository(repo)

    agent = get_agent()
    tools = [git_clone, git_list_dir, git_read_file, write_file, run_sh_command]

    agent_executor = AgentExecutor(agent=agent, tools=tools, handle_parsing_errors=True)
    agent_executor.invoke({"input": repo})


if __name__ == "__main__":
    main()
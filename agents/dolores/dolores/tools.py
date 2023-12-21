# stdlib
from typing import List
import os

# 3rd party
from langchain.tools import StructuredTool

# local
from workspace import Workspace
from system import SystemEnvironment, MissingSystemEnvError
from chains import summarize_qa_git, summarize_qa_log


def get_search_path_tool(workspace: Workspace) -> StructuredTool:
    def search_path(path: str) -> str:
        """
        Efficiently search for files and directories using this tool,
        which allows you to specify a path and employ glob patterns
        for advanced queries. Searches begin at the top-level of the
        cloned repository.
        """
        try:
            results = workspace.search_path(path)
            return "\n".join(results)
        except ValueError as e:
            return str(e)

    return StructuredTool.from_function(search_path)


def get_read_file_tool(workspace: Workspace) -> StructuredTool:
    def file_qa(question: str, filepath: str) -> str:
        """
        Input a question and a filename. File paths are relative to the top-level
        of the GitHub repository. The function scans the file, extracts
        relevant data to your question, and creates a detailed prompt.
        It then utilizes this prompt to deliver a well-informed and accurate response.
        """
        try:
            text = workspace.read_file(filepath)
            return summarize_qa_git(question, text, filepath)
        except ValueError as e:
            return str(e)

    return StructuredTool.from_function(file_qa)


def get_read_log_tool(env: SystemEnvironment) -> StructuredTool:
    def log_qa(question: str, log_id: str) -> str:
        """
        Use this tool to analyze the log file from running a command.
        Provide your question and the `log_id` from the command run.
        The tool scans the log in segments, extracting relevant details
        to answer your query.
        """
        try:
            text = env.read_log(log_id=log_id)
            filepath = os.path.join(env.logs_dir, log_id)
            return summarize_qa_log(question, text, filepath)
        except ValueError as e:
            return str(e)

    return StructuredTool.from_function(log_qa)


def get_init_env_tool(env: SystemEnvironment) -> StructuredTool:
    def init_env() -> str:
        """
        Initializes an environment where commands can be tested on the repository.
        A fresh copy of the repository is cloned into the environment. Running
        this function discards previously initialized environments. This function
        must be run at least once before running any commands.
        """
        return env.init_env()
    
    return StructuredTool.from_function(init_env)


def get_exec_command_tool(env: SystemEnvironment) -> StructuredTool:
    def exec_command(command: str) -> str:
        """
        Executes the provided command in the current environment. The current working
        directory of each command is set to the top-level directory of the repository.
        An environment must be initialized with init_env before this function can be run.
        The effects of running commands in the repository persist until the next call to
        init_env, which will reset the environment with a fresh clone of the system.
        You should reset the environment often when the effects of commands do not require
        persistence in order to ensure commands are running on fresh copies of the repository.

        The function returns the return code of the command, stdout, stdin, and a log id
        that can be used to lookup the output of the command at any time.
        """
        try:
            result = env.exec(command)
            stdout, stderr = result["stdout"], result["stderr"]
            if len(stdout) > 1000:
                stdout = "[Too long. See log file for full output]"
            if len(stderr) > 1000:
                stderr = "[Too long. See log file for full output]"

            return f"""
                Return code: {result["returncode"]}
                Log id: {result["log_id"]}
                stdout: {stdout},
                stderr: {stderr}
            """
        except (ValueError, MissingSystemEnvError) as e:
            return str(e)

    return StructuredTool.from_function(exec_command)


def get_tools(workspace: Workspace, env: SystemEnvironment) -> List[StructuredTool]:
    return [
        get_search_path_tool(workspace),
        get_read_file_tool(workspace),
        get_read_log_tool(env),
        get_init_env_tool(env),
        get_exec_command_tool(env)
    ]

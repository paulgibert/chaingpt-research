# stdlib
from typing import List
import argparse

# 3rd party
from yaspin import yaspin
from yaspin.spinners import Spinners
from langchain.chat_models import ChatOpenAI
from langchain.agents.initialize import initialize_agent
from langchain.agents.agent_types import AgentType
from langchain.memory import ConversationBufferMemory
from langchain.prompts import MessagesPlaceholder

# local
from workspace import Workspace
from system import SystemEnvironment
from tools import get_tools


def _parse_args() -> argparse.Namespace:
    """
    Parse arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--repository",
                        help="The GitHub repository to use. Must include the .git",
                        required=True)
    return parser.parse_args()


def run_agent():
    # Create workspace
    url = _parse_args().repository
    workspace = Workspace(url)
    env = SystemEnvironment(url)

    # Create the agent
    tools = get_tools(workspace, env)

    llm = ChatOpenAI(temperature=0, model="gpt-4")


    agent_kwargs = {
        "extra_prompt_messages": [MessagesPlaceholder(variable_name="memory")],
    }

    memory = ConversationBufferMemory(memory_key="memory", return_messages=True)

    context = f"""
    As an OpenAI experting and extremely intelligent engineering assistant focusing on the {url} GitHub repository,
    your key role is to engage with engineers, offering precise and reliable
    information about repository-related issues. You are equipped with specialized
    tools for searching file names, reading files, and particularly executing
    commands within the repository. Your responses should be concise yet thorough,
    backed by diligent verification using these tools. You are expected to research exhaustively
    and consider multiple perspectives before finalizing an answer, demonstrating your commitment
    to accuracy and detail in engineering problem-solving. 
    """

    agent = initialize_agent(
        tools, llm, agent=AgentType.OPENAI_FUNCTIONS,
        agent_kwargs=agent_kwargs,
        memory=memory, context_prompt=context,
        verbose=True
    )

    while True:
        question = input("Question: ")
        if question == "exit":
            exit()
        if question == "sh":
            workspace.start_shell()
        output = agent.run(context + question)
        print(output)

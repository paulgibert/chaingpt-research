import os
from langchain.tools.render import format_tool_to_openai_function
from langchain.chat_models import ChatOpenAI
from langchain.agents.format_scratchpad import format_to_openai_functions
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from tools import git_clone, git_list_dir, git_read_file, write_file, run_sh_command
from utils import load_openai_api_key


os.environ["OPENAI_API_KEY"] = load_openai_api_key()

MODEL = "gpt-4"
TEMPERATURE = 0


def get_agent():
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system",
                """
                Your goal is to write a bash file that builds the project located at the provided GitHub repository from source.
                You will accomplish this by following this strategy:

                1) Clone the repository
                2) Search the repository for documentation and build files
                3) Test commands to make sure they work and resolve errors
                4) The final command of the bash file should start the build process.
                   Be sure to examine the output of any build commands you run to ensure
                   something was actually built. Try running the output binary or examining
                   the output for build logs. Build commands that return zero or little text
                   are not valid and you should keep exploring.
                5) Once you have verified the needed build commands, write them to a bash file
                   called \"build.sh\".
                """
            ),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    tools = [git_clone, git_list_dir, git_read_file, write_file, run_sh_command]
    llm = ChatOpenAI(model=MODEL, temperature=TEMPERATURE) \
            .bind(functions=[format_tool_to_openai_function(t) for t in tools])

    agent = (
        {
            "input": lambda x: x["input"],
            "agent_scratchpad": lambda x: format_to_openai_functions(x["intermediate_steps"])
        }
        | prompt
        | llm
        | OpenAIFunctionsAgentOutputParser()
    )

    return agent

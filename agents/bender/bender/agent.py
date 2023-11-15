from typing import List, Dict
from operator import itemgetter
import logging
from langchain.callbacks import get_openai_callback
from langchain.tools.render import format_tool_to_openai_function
from langchain.agents.format_scratchpad import format_to_openai_functions
from langchain.chat_models import ChatOpenAI
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import BaseTool
from langchain.agents import AgentExecutor
from utils import tags


# Params for the agent model
MODEL = "gpt-4"
TEMPERATURE = 0


def _make_agent_chain(system_prompt: str, inputs: List[str],
                     tools: List[BaseTool]) -> any:
    """
    Create a LangChain chain for an OpenAI functions agent.
    """
    # Compile the prompt with input names
    user_prompt = "".join(["\n" + tags(i) + "\n" for i in inputs])
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("user", user_prompt),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    # Define the llm and bind tools
    llm = ChatOpenAI(model=MODEL, temperature=TEMPERATURE) \
            .bind(functions=[format_tool_to_openai_function(t) for t in tools])

    # Define the input schema
    input_ = {i: itemgetter(i) for i in inputs}
    input_.update({"agent_scratchpad":
                 lambda x: format_to_openai_functions(x["intermediate_steps"])
                 })

    # Create the chain
    return (
        input_
        | prompt
        | llm
        | OpenAIFunctionsAgentOutputParser()
    )


class Agent:
    """
    An object representing an LLM agent
    """
    def __init__(self, prompt: str, inputs: List[str], tools: List[BaseTool]):
        """
        @param prompt: The primary prompt defining the agent's task
        @param inputs: The names of the inputs that the agent will receive
        @param tools: The tools the agent can use to complete the task
        """
        self.prompt = prompt
        self.inputs = inputs
        self.tools = tools
        self._chain = _make_agent_chain(prompt, inputs, tools)
  
    def run(self, inputs: Dict[str, str], verbose: bool=False) -> str:
        """
        Runs the agent with the given inputs

        @param inputs: A Dict of inputs. The keys are the name of the inputs as
                       provided in the Agent class constructor.
        @param verbose: If True, will print the logs of LangChain's agent runtime
        @return response: The response from the agent after completing the task
        """
        agent_executor = AgentExecutor(agent=self._chain,
                                       tools=self.tools,
                                       handle_parsing_errors=True,
                                       max_iterations=50,
                                       verbose=verbose)
        with get_openai_callback() as cb:
            result = agent_executor.invoke(inputs)
            logging.info(f"Agent callback:\n{str(cb)}")
            return result

from typing import List, Dict
from operator import itemgetter
from langchain.tools.render import format_tool_to_openai_function
from langchain.agents.format_scratchpad import format_to_openai_functions
from langchain.chat_models import ChatOpenAI
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import BaseTool
from langchain.agents import AgentExecutor


MODEL = "gpt-4"
TEMPERATURE = 0


def tags(label: str) -> str:
    """
    <label>
    {label}
    </label>
    """
    return f"<{label}>" + "\n{" + label + "}\n" + f"</{label}>"


def make_agent_chain(system_prompt: str, inputs: List[str],
                     tools: List[BaseTool]) -> any:
    user_prompt = "".join(["\n" + tags(i) + "\n" for i in inputs])
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("user", user_prompt),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    llm = ChatOpenAI(model=MODEL, temperature=TEMPERATURE) \
            .bind(functions=[format_tool_to_openai_function(t) for t in tools])

    input_ = {i: itemgetter(i) for i in inputs}
    input_.update({"agent_scratchpad":
                 lambda x: format_to_openai_functions(x["intermediate_steps"])
                 })
    return (
        input_
        | prompt
        | llm
        | OpenAIFunctionsAgentOutputParser()
    )


class Agent:
    def __init__(self, prompt: str, inputs: List[str], tools: List[BaseTool]):
        self.prompt = prompt
        self.inputs = inputs
        self.tools = tools
        self._chain = make_agent_chain(prompt, inputs, tools)
    
    def run(self, inputs: Dict[str, str], verbose: bool=False) -> str:
        agent_executor = AgentExecutor(agent=self._chain,
                                       tools=self.tools,
                                       handle_parsing_errors=True,
                                       max_iterations=50,
                                       verbose=verbose)
        return agent_executor.invoke(inputs)

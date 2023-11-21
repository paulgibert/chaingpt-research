from typing import List
from operator import itemgetter
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.document import Document
from .response import LLMResponse
from .utils import invoke_chain, IDK_TOKEN


MODEL = "gpt-4"
TEMPERATURE = 0
PROMPT_TEXT = """
I need instructions on how to build a software project from source.
Below is the documentation from the project's repository and the Makefile,
if applicable. I require the response in JSON format with the following
fields: a 'summary' containing a brief description of the build
process, a 'dependencies' field listing all necessary dependencies,
and a 'shell' field providing the exact commands needed to build
the project. Please note that the build instructions should not include
steps for cloning the repository or changing directories. Assume we are
already in the correct directory on the correct branch. The instructions
should be precise, clear, and directly executable.

In cases of multiple build methods, always prioritize the process as
outlined in the documentation. If the documentation does not specify
or is incomplete, refer to the Makefile. If neither source provides
sufficient information, respond with '%s' instead of any JSON.

<documentation>
{docs}
</documentation>

<makefile>
{makefile}
</makefile>
""" % IDK_TOKEN



def build_steps_from_llm(package: str, version: str,
                         docs: List[Document],
                         makefile: str=None) -> LLMResponse:
    """
    Asks the LLM to generate build instructions for the package
    given the provided documentation. A Makefile summary can also
    be optional specified.

    Uses `gpt-4` with `temperature=0`

    @param package: package name
    @param version: package version
    @param docs: A `List` of LangChain `Document`s containing build information
    @param makefile: A summary of the contents of a Makefile.
    @returns An `LLMResponse` with build instructions. If no
             description could be generated, `LLMResponse.output`
             is set to `None`.
    """
    if makefile is None:
        makefile = "The project does not have a Makefile."

    prompt = PromptTemplate.from_template(PROMPT_TEXT)
    llm = ChatOpenAI(model=MODEL,
                     temperature=TEMPERATURE)
    chain = (
        {"package": itemgetter("package"),
         "version": itemgetter("version"),
         "docs": lambda x: "\n\n".join([
             d.page_content for d in x["docs"]]),
         "makefile": itemgetter("makefile")}
        | prompt
        | llm
        | StrOutputParser()
    )

    inputs = {
        "package": package,
        "version": version,
        "docs": docs,
        "makefile": makefile
    }
    return invoke_chain(chain, inputs)

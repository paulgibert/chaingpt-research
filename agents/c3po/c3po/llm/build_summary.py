from typing import List
from operator import itemgetter
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.document import Document
from .response import LLMResponse
from .utils import invoke_chain


MODEL = "gpt-4"
TEMPERATURE = 0
BASE_PROMPT_TEXT = """
You're goal is to describe how to build version {version}
of the {package} software project from source. Give your
response in exactly three parts.

Part 1 is a short description that describes the general build process.

Part 2 is the list of dependencies/build tools that will be necessary to
build the project.

Part 3 is a detailed list of shell commands that a user can follow to
build the project. You may assume that the git commands to clone and
navigate into the project's git repository have already been executed
and all build dependencies are already installed.

Do not include any additional content outside of the 3 parts defined.

You are provided the following excerpts from the repositories documentation
to reference when generating build instructions.

<documentation>
{docs_content}
</documentation>
"""

MAKEFILE_PROMPT_ADDON_TEXT = """
The repository also has a Makefile. A summary of the contents
of the Makefile are provided below. Often times there are several
ways to build a project from source. You should always prioritize
what the documentation recommends. If the documentation does not
discuss building from source, prioritize using the Makefile before
considering other methods.

<makefile>
{makefile_content}
</makefile
"""


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
    if makefile is not None:
        prompt = PromptTemplate.from_template(BASE_PROMPT_TEXT + MAKEFILE_PROMPT_ADDON_TEXT)
    else:
        prompt = PromptTemplate.from_template(BASE_PROMPT_TEXT)

    llm = ChatOpenAI(model=MODEL,
                     temperature=TEMPERATURE)
    chain = (
        {"package": itemgetter("package"),
         "version": itemgetter("version"),
         "docs_content": lambda x: "\n\n".join([
             d.page_content for d in x["docs"]]),
         "makefile_content": itemgetter("makefile")}
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

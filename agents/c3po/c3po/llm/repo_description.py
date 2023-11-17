from operator import itemgetter
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.schema.output_parser import StrOutputParser
from .response import LLMResponse
from .utils import invoke_chain, IDK_TOKEN


MODEL = "gpt-4"
TEMPERATURE = 0
PROMPT_TEXT = """
You are creating an APK build package for
the {package} software project (version {version}).
Given the provided excerpts from various documentation
files found in the repository of the source code, generate
a short, 1 sentence description of what the software is for
the build file. Only respond with the description.

If the provided excerpts do not contain enough
information or are irrelevant are you familiar with
{package}? If so, generate your own description for it
without referencing the provided content. Again, only
respond with the description.

If you are unfamiliar with the package and have not been provided
with sufficient information on it respond with '%s' only.

<excerpts>
{content}
</excerpts>
""" % IDK_TOKEN


def repo_description_from_llm(package: str, version: str,
                              content: str) -> LLMResponse:
    """
    Asks the LLM to generate a description of the package
    given the provided content from documentation. The LLM
    is also provided with the package name and version so that
    it can leverage its training data as well.

    Uses `gpt-4` with `temperature=0`

    @param package: package name
    @param version: package version
    @param content: The content to reference
    @returns An `LLMResponse` with the description. If no
             description could be generated, `LLMResponse.output`
             is set to `None`.
    """
    prompt = PromptTemplate.from_template(PROMPT_TEXT)
    llm = ChatOpenAI(model=MODEL,
                     temperature=TEMPERATURE)
    chain = (
        {"package": itemgetter("package"),
         "version": itemgetter("version"),
         "content": itemgetter("content")}
        | prompt
        | llm
        | StrOutputParser()
    )

    inputs = {
        "package": package,
        "version": version,
        "content": content,
    }
    return invoke_chain(chain, inputs)

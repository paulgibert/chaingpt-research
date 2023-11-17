from operator import itemgetter
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.schema.output_parser import StrOutputParser
from .response import LLMResponse
from .utils import invoke_chain, IDK_TOKEN


MODEL = "gpt-4"
TEMPERATURE = 0
MAX_CONTENT_LEN = 1000
PROMPT_TEXT = """
You are creating an APK build package for
the {package} software project (version {version}).
Given the provided excerpts from various documentation
files found in the repository of the source code, report
what the license used is. Response with only the license
name. If the provided excerpts do not contain enough information
to determine the license, respond with '%s' only.

<excerpts>
{content}
</excerpts>
""" % IDK_TOKEN


def _check_content(content: str):
    if len(content) > MAX_CONTENT_LEN:
        raise ValueError(f"Size of `content` exceeds max allowed value of {MAX_CONTENT_LEN}")


def repo_description_from_llm(package: str, version: str,
                              content: str) -> LLMResponse:
    """
    Asks the LLM to the license of the package
    given the provided content from documentation. The LLM
    is also provided with the package name and version so that
    it can leverage its training data as well.

    Uses `gpt-4` with `temperature=0`

    @param package: package name
    @param version: package version
    @param content: The content to reference
    @returns An `LLMResponse` with the license. If a license
             could not be determined, `LLMResponse.output`
             is set to `None`.
    @raises `ValueError` if size of `content` is too large
    """
    _check_content(content)

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

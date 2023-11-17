from operator import itemgetter
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.schema.output_parser import StrOutputParser
from .response import LLMResponse
from .utils import invoke_chain, IDK_TOKEN


MODEL = "gpt-4"
TEMPERATURE = 0
PROMPT_TEXT = """
What is the license used by the software
project {package} version {version}? Below is
some excerpts from the project's documentation
to help you find the answer. Respond with only
the license name in all lowercase with no spaces.
If you don't know the answer, respond with '%s' only.

<excerpts>
{content}
</excerpts>
""" % IDK_TOKEN


def repo_license_from_llm(package: str, version: str,
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
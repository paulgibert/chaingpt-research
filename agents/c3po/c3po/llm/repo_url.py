from operator import itemgetter
import re
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.schema.output_parser import StrOutputParser
from .response import LLMResponse
from .utils import invoke_chain, IDK_TOKEN


MODEL = "gpt-4"
TEMPERATURE = 0
MAX_PKG_LEN = 32
PROMPT_TEXT = """
What is the GitHub repository url for
the {package} software project? Only respond
with the url. If you do not know the answer
reply with '%s' only.
""" % IDK_TOKEN


def _check_package(package: str):
    """
    Checks that the package name is short and properly formatted
    """
    if len(package) > MAX_PKG_LEN:
        raise ValueError(f"Package name {package} is too long. Must be <= {MAX_PKG_LEN}")
    pattern = r"^[a-zA-Z0-9\-_]+$"
    if re.match(pattern, package) is None:
        raise ValueError(f"The package name {package} is not properly formatted")


def repo_url_from_llm(package:str) -> LLMResponse:
    """
    Asks an LLM what the GitHub repo url is given a package name.
    A correct answer or any answer at all is not guaranteed.

    Uses `gpt-4` with `temperature=0`

    @param package: The package to ask about
    @returns an LLMResponse with the repository url
    @raises ValueError if the package name is too long or improperly
            formatted
    """
    _check_package(package)
    prompt = PromptTemplate.from_template(PROMPT_TEXT)
    llm = ChatOpenAI(model=MODEL,
                     temperature=TEMPERATURE)
    chain = (
        {"package": itemgetter("package")}
        | prompt
        | llm
        | StrOutputParser()
    )

    return invoke_chain(chain, {"package": package})

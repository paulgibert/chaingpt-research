from operator import itemgetter
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.schema.output_parser import StrOutputParser
from .response import LLMResponse
from .utils import invoke_chain, IDK_TOKEN


MODEL = "gpt-4"
TEMPERATURE = 0
PROMPT_TEXT = ("""
What is the GitHub repository url for
the {package} software project? Only respond
with the url. If you do not know the answer
reply with '%s' only.
""" % IDK_TOKEN)


def repo_url_from_llm(package:str) -> LLMResponse:
    """
    Asks an LLM what the GitHub repo url is given a package name.
    A correct answer or any answer at all is not guaranteed.

    Uses GPT-4 with `temperature=0`

    @param package: The package to ask about
    @returns an LLMResponse with the repository url 
    """
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
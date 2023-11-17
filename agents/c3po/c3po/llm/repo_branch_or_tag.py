from typing import List
from operator import itemgetter
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.schema.output_parser import StrOutputParser
from c3po.repo.validate import check_branch_or_tag
from .response import LLMResponse
from .utils import invoke_chain, IDK_TOKEN


MODEL = "gpt-4"
TEMPERATURE = 0
MAX_N_BRANCHES_AND_TAGS = 1000
PROMPT_TEXT = """
Which branch or tag should I checkout in order to build
version {version} of the software project {package} from source?
The available branches and tags are provided below. Only respond with
a single branch or tag name from the list.
If you do not know the answer reply with '%s' only.
               
<branches>
{branches}
</branches>
               
<tags>
{tags}
</tags>
""" % IDK_TOKEN


def _check_len(branches: List[str], tags: List[str]):
    """
    Raises a ValueError if max number of branches and tags is
    succeeded
    """
    if len(branches) + len(tags) > MAX_N_BRANCHES_AND_TAGS:
        raise ValueError("Too many branched and tags for LLM")


def _check_formatting(branches: List[str], tags: List[str]):
    """
    Raises a ValueError if any branch or tag names are malformed
    """
    for bt in branches + tags:
        check_branch_or_tag(bt)


def repo_branch_or_tag_from_llm(package:str, version: str,
                                branches: List[str],
                                tags: List[str]) -> LLMResponse:
    """
    Asks an LLM which branch or tag to checkout for the provided
    package and version.

    Uses `gpt-4` with `temperature=0`

    @param package: The package to ask about
    @param version: The version to find a branch or tag for
    @param branches: A `List` of branch names
    @param tags: A `List` of tag names
    @returns an `LLMResponse` with the suggested branch or tag. If no
             branch or tag is suggested, `LLMResponse.output` is set to `None`.
    @raises `ValueError` if too many branches and tags are provided (max 1000 combined)
    """
    # Do nothing if there are 0 branches and tags
    if len(branches) + len(tags) == 0:
        return LLMResponse(0, 0, 0, 0, None)

    _check_len(branches, tags)
    _check_formatting(branches, tags)

    prompt = PromptTemplate.from_template(PROMPT_TEXT)
    llm = ChatOpenAI(model=MODEL,
                     temperature=TEMPERATURE)
    chain = (
        {"package": itemgetter("package"),
         "version": itemgetter("version"),
         "branches": lambda x: ", ".join(x["branches"]),
         "tags": lambda x: ", ".join(x["tags"])}
        | prompt
        | llm
        | StrOutputParser()
    )

    inputs = {
        "package": package,
        "version": version,
        "branches": branches,
        "tags": tags
    }
    return invoke_chain(chain, inputs)

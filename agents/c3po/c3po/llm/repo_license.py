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
LICENSE_MAX_SZ = 1000
PROMPT_TEXT = """
According to the provided content, what software
license is in use? Respond with the license name
only, in all lowercase, and without spaces. If the
content does not mention the license in use, respond with
'%s' only.

<content>
{content}
</content>
""" % IDK_TOKEN


def repo_license_from_llm(license:str=None, docs: List[Document]=None) -> LLMResponse:
    """
    Provides either the contents of a license file or a `List` of
    relevant `Document`s to an LLM and asks for the license in use.

    Uses `gpt-4` with `temperature=0`

    @param license: The contents of a license file. This parameter
                    is truncated to the first 1000 characters as the
                    beginning of a license file almost always contains
                    its name.
    @param docs: A `List` of `Documents` containing references to the license
                in use. Ignored if `license` is provided.
    @returns An `LLMResponse` with the license. If a license
             could not be determined, `LLMResponse.output`
             is set to `None`.
    """
    prompt = PromptTemplate.from_template(PROMPT_TEXT)
    llm = ChatOpenAI(model=MODEL,
                     temperature=TEMPERATURE)
    chain = (
        {"content": itemgetter("content")}
        | prompt
        | llm
        | StrOutputParser()
    )

    if license is not None:
        inputs = {
            "content": license[LICENSE_MAX_SZ:]
        }
    elif docs is not None:
        inputs = {
            "content": "\n\n".join(d.page_content for d in docs)
        }
    else:
        raise ValueError("Must provide either `license` or `docs`")
    return invoke_chain(chain, inputs)

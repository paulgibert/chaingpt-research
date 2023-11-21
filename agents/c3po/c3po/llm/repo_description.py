from typing import List
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.document import Document
from .response import LLMResponse
from .utils import invoke_chain, IDK_TOKEN


MODEL = "gpt-4"
TEMPERATURE = 0
PROMPT_TEXT = """
I am providing a snippets of documentation from a GitHub
repository below. Based on this documentation, please
generate a one-sentence description that captures the
essence of the repository. This description should be
succinct and clear, ideally suited for use as a package
description, emphasizing the primary purpose and a key
feature of the project. Do not begin the description with
the subject's name. If a description can't be generated from
the provided documentation, respond with '%s' only.

<docs>
{content}
</docs>
""" % IDK_TOKEN


def repo_description_from_llm(docs: List[Document]) -> LLMResponse:
    """
    Asks the LLM to generate a description of the package
    given a `List` of `Document`s.

    Uses `gpt-4` with `temperature=0`

    @param docs: The `List` of `Document`s
    @returns an `LLMResponse` with a description. If no
             description could be generated,
             `LLMResponse.output` is set to `None`.
    """
    prompt = PromptTemplate.from_template(PROMPT_TEXT)
    llm = ChatOpenAI(model=MODEL,
                     temperature=TEMPERATURE)
    chain = (
        {"content": lambda x: "\n\n".join([
            d.page_content for d in x["docs"]])}
        | prompt
        | llm
        | StrOutputParser()
    )

    return invoke_chain(chain, {"docs": docs})

from typing import List
from operator import itemgetter
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.output_parsers.list import ListOutputParser
from .response import LLMResponse
from .utils import invoke_chain


MODEL = "gpt-4"
TEMPERATURE = 0
# TODO: This prompt does not handle the case where directory is potentially relevant
# even though the file name is not. Example /src/build-instructions/apple.txt
PROMPT_TEXT = """
Given a list of file paths in the project's GitHub
repository, respond with a list of any files that may
contain any documentation about the project, especially documentation
describing how to build from source. To determine if a file might contain
relevant information, pay attention to both the file name and the names of
the directories in its path. For example, a file might have a random name
but be located under the docs/ directory, making it relevant. When in doubt,
include the file. Your response should only contain a comma separated list of
the selected file paths. Use commas as the only delimiter (no extra spaces)
and do not surround the values of the list with quotes. If none of the provided 
file paths are likely to contain relevant information to
the build process, respond with an empty string only.

<files>
{file_paths}
</files>
"""


class _CommaSeparatedListOutputParser(ListOutputParser):
    """
    Parses a comma separated LLM output to a `List`.
    Fixes bug in LangChain's `CommaSeparatedListOutputParser`
    where empty response are not parsed correctly.
    """
    def parse(self, text: str):
        text_stripped = text.strip(", ")
        if len(text_stripped) == 0:
            return []
        return [e.strip(" ") for e in text_stripped.split(",")]


def repo_doc_files_from_llm(file_paths: List[str]) -> LLMResponse:
    """
    Asks the LLM to identify build documentation files
    given the full paths of files from a repository. 

    Uses `gpt-4` with `temperature=0`

    @param file_paths: The list of file_paths to consider
    @returns A refined `List` containing the paths to build documentation.
             If not documentation is identified, and empty `List` is
             returned.
    """
    prompt = PromptTemplate.from_template(PROMPT_TEXT)
    llm = ChatOpenAI(model=MODEL,
                     temperature=TEMPERATURE)
    chain = (
        {"file_paths": itemgetter("file_paths")}
        | prompt
        | llm
        | _CommaSeparatedListOutputParser()
    )

    return invoke_chain(chain, {"file_paths": file_paths})

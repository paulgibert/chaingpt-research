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
"I have a list of file paths from a software project repository and
need to identify which paths are likely to contain text-based documentation
about how to package the project. The list will be used to build a vector
store that will be queried for information about packaging the project.
It's crucial to select only the relevant documentation and avoid including
code or irrelevant documentation. Please consider both the file names and
the directories they are in, as both can provide insights into the content
and relevance of the files.

Criteria for Selection:
- Include only text-based documentation. Exclude source code, binary files,
  and files like Makefiles, even if they contain build-related information.
- The file name and its directory context are important. For example,
  files in a '/docs' directory are more likely to be relevant than those
  in a '/src' directory.

<files>
{file_paths}
</files>

Please analyze the file paths and identify which ones should be
included in the vector store for information about packaging the project.

Your response should only include a comma separated list of file path strings.
If no file paths should be included, return the empty string ''."

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
        return [e.strip(" '\"") for e in text_stripped.split(",")]


def repo_doc_files_from_llm(file_paths: List[str]) -> LLMResponse:
    """
    Asks the LLM to identify build documentation files
    given the full paths of files from a repository. 

    Uses `gpt-4` with `temperature=0`

    @param file_paths: The list of file_paths to consider
    @returns An `LLMResponse` containing the paths to build documentation.
             If no paths are identified, `LLMResponse.output`
             is set to an empty `List`.
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

from typing import List
from operator import itemgetter
from tqdm import tqdm
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from langchain.schema.output_parser import StrOutputParser
from .response import LLMResponse
from .utils import invoke_chain


MODEL = "gpt-4"
TEMPERATURE = 0
CHUNK_SIZE = 3000
CHUNK_OVERLAP = 1000
PROMPT_TEXT = """
I am analyzing a Makefile chunk by chunk to identify the most
relevant targets for compiling and building a software project
from source. The goal is to maintain a running list of the top 5
most relevant targets, including the target name and a brief description
of what it accomplishes. Below is the latest chunk of the Makefile
along with the current list of top targets identified from previous
chunks. Please analyze the new chunk and update the list, ensuring it
contains up to 5 of the most relevant targets. If fewer than 5
relevant targets are found, or if no relevant targets are in this
chunk, do not update the list. Only include the list in your response.

<chunk>
{chunk}
</chunk>

<list>
{summary}
</list>

"""


def _split(file_path: str) -> List[Document]:
    """
    Loads the provided file and splits it into chunks.
    """
    loader = TextLoader(file_path)
    splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE,
                                              chunk_overlap=CHUNK_OVERLAP)
    return loader.load_and_split(splitter)


def makefile_summary_from_llm(file_path: List[str]) -> LLMResponse:
    """
    Summarizes a Makefile. 

    Uses `gpt-4` with `temperature=0`

    @param file_path: The path to the Makefile
    @returns an `LLMResponse` with the Makefile summary.
    """
    prompt = PromptTemplate.from_template(PROMPT_TEXT)
    llm = ChatOpenAI(model=MODEL,
                     temperature=TEMPERATURE)
    chain = (
        {"summary": itemgetter("summary"),
         "chunk": lambda x: x["chunk"].page_content}
        | prompt
        | llm
        | StrOutputParser()
    )

    summary = ""
    for doc in tqdm(_split(file_path), desc="Refining Makefile"):
        response = invoke_chain(chain, {"summary": summary,
                                        "chunk": doc})
        summary = response.output
    # TODO: This response does not contain any token usage information
    # about the previous responses used during refine.
    return response

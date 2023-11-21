from typing import List
from operator import itemgetter
from tqdm import tqdm
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.schema.output_parser import StrOutputParser
from .response import LLMResponse
from .utils import invoke_chain, split_file


MODEL = "gpt-4"
TEMPERATURE = 0
CHUNK_SIZE = 3000
CHUNK_OVERLAP = 1000
PROMPT_TEXT = """
I am analyzing a file chunk by chunk to identify the most
relevant information according to a query. Below is the query, 
the latest chunk of the file, and a summary of the relevant information
identified from previous chunks. Please analyze the new chunk and
update the summary, ensuring it contains the most relevant information.
If no relevant information is found do not update the summary.
Only include the summary in your response. If the summary is empty and
you have no information to contribute, return nothing (an empty string).

<query>
{query}
</query>

<chunk>
{chunk}
</chunk>

<summary>
{summary}
</summary>

"""


def query_file_with_llm(query: str, file_path: List[str]) -> LLMResponse:
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
        {"query": itemgetter("query"),
         "chunk": lambda x: x["chunk"].page_content,
         "summary": itemgetter("summary")}
        | prompt
        | llm
        | StrOutputParser()
    )

    summary = ""
    chunks = split_file(file_path, chunk_size=CHUNK_SIZE,
                        chunk_overlap=CHUNK_OVERLAP)
    for doc in tqdm(chunks, desc="Refining file"):
        inputs = {
            "query": query,
            "chunk": doc,
            "summary": summary
        }
        response = invoke_chain(chain, inputs)
        summary = response.output
    # TODO: This response does not contain any token usage information
    # about the previous responses used during refine.
    return response

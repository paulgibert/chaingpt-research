from typing import List
import os
import asyncio
from langchain.prompts import PromptTemplate
from langchain.schema.document import Document
from langchain.chat_models import ChatOpenAI
from langchain.schema.output_parser import StrOutputParser
from tqdm.asyncio import tqdm
from yaspin import yaspin
from yaspin.spinners import Spinners
from .utils import check_language, split_file


CHUNK_SIZE = 4000
CHUNK_OVERLAP = 250
MODEL_REFINE = "gpt-3.5-turbo-1106"
MODEL_AGG = "gpt-4"
MODEL_TEMP = 0


CHUNK_REFINE_PROMPT = """
You are scanning the provided chunk of a document
in an attempt to answer the provided query. You will
summarize this chunk which will be combined with the
summaries of other chunks to derive a final answer
to the query. Given the provided chunk, include any
and all relevant information to the query in the summary.
If there is no relevant info in the chunk, respond with
only an empty string. Otherwise, make your summaries
detailed and terse.

<query>
{query}
</query

<chunk>
{chunk}
</chunk>
                                  
Summary:


"""

CHUNK_AGG_PROMPT = """
A large document was believed to contain information
that could help answer the provided query. This document
was split into overlapping chunks which were independently
summarized with an emphasis on information pertaining to the
query. Your goal is to combine these summaries into one larger,
detailed summary that contains all relevant information to
the query. Respond with only this aggregated summary. Be sure
to carry over all details but omit duplicate information.
                                  
<summaries>
{summaries}
</summaries>
                                  
<query>
{query}
</query>
                                  
Aggregate summary:
                          
"""


async def _ainvoke_chain(chain, input, delay) -> str:
    await asyncio.sleep(delay)
    response = await chain.ainvoke(input)
    return response


async def _refine_chunks(docs: List[Document], query: str) -> List[str]:
    prompt = PromptTemplate.from_template(CHUNK_REFINE_PROMPT)
    llm = ChatOpenAI(temperature=MODEL_TEMP,
                     model=MODEL_REFINE)
    chain = (
        {
        "query": lambda x: x["query"],
        "chunk": lambda x: x["doc"].page_content
        }
        | prompt
        | llm
        | StrOutputParser()
    )
    
    tasks = []
    for i, d in enumerate(docs):
        t = _ainvoke_chain(chain, {"query": query, "doc": d}, delay=4*i)
        tasks.append(t)
    return await tqdm.gather(*tasks, desc="Refining")


def _agg_summaries(summaries: List[str], query: str) -> str:
    prompt = PromptTemplate.from_template(CHUNK_AGG_PROMPT)
    llm = ChatOpenAI(temperature=MODEL_TEMP,
                     model=MODEL_AGG)
    chain = (
        {
        "summaries": lambda _: "\n\n".join(summaries),
        "query": lambda x: x["query"],
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    with yaspin(Spinners.line, text="Summerizing"):
        return chain.invoke({"summaries": summaries, "query": query})


def refine_and_read(path: str, query: str, language: str=None) -> str:
    """
    Equivalent to the file_refine_text function with the added
    feature of being able to supply a language. The language is used
    to more intelligently split the document than file_store_lookup_text
    would. The supported langauges are: cpp, go, java, kotlin, js, ts,
    php, proto, python, rst, ruby, rust, scala, swift, markdown, latex,
    html, sol, and csharp. In addition to the errors returned from
    file_refine_text, this function will also report an error if
    an unsupported langauge is provided.
    """
    if not os.path.exists(path):
        raise FileNotFoundError
    if language is not None:
        check_language(language)
    if language == "text":
        language = None # Do nothing for language=text
    docs = split_file(path, chunk_size=CHUNK_SIZE,
                      chunk_overlap=CHUNK_OVERLAP,
                      language=language)
    summaries = asyncio.run(_refine_chunks(docs, query))
    return _agg_summaries(summaries, query)

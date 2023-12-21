# stdlib
from operator import itemgetter
import os

# 3rd party
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import TextLoader
from langchain_core.output_parsers import StrOutputParser


def _summarize_qa(question: str, text: str, filepath: str, prompt_context: str) -> str:
    document_prompt = prompt_context + """
    You are analyzing the file chunk by chunk in order
    to answer the question '{question}'. Summarize the provided chunk, including
    any information relevant to the question. If the chunk contains no relevant information,
    respond with an empty string.

    Chunk:

    {chunk}
    """

    summarize_prompt = prompt_context + """You scanned the file chunk by chunk, summarizing each chunk
    for information to answer the question '{question}'. The summarized chunks are provided below.
    Using these summaries, answer the provided question. If the summaries do not contain information
    relevant to the question, reply that there is not enough information in the file to provide an answer.

    summaries:

    {summaries}
    """


    splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=500)
    docs = splitter.split_text(text)
    llm = ChatOpenAI(model="gpt-4", temperature=0)

    document_chain = ({
        "filename": itemgetter("filename"),
        "filepath": itemgetter("filepath"),
        "question": itemgetter("question"),
        "chunk": itemgetter("chunk")}
        | PromptTemplate.from_template(document_prompt)
        | llm
        | StrOutputParser()
    )

    summarize_chain = ({
        "filename": itemgetter("filename"),
        "filepath": itemgetter("filepath"),
        "question": itemgetter("question"),
        "summaries": lambda x: "\n\n".join(x["summaries"])}
        | PromptTemplate.from_template(summarize_prompt)
        | llm
        | StrOutputParser()
    )

    inputs = [{
        "filename": os.path.basename(filepath),
        "filepath": filepath,
        "question": question,
        "chunk": doc
    } for doc in docs]

    summaries = document_chain.batch(inputs)
    return summarize_chain.invoke({
        "filename": os.path.basename(filepath),
        "filepath": filepath,
        "question": question,
        "summaries": summaries
    })


def summarize_qa_git(question: str, text: str, filepath: str) -> str:
    context = """
    You are scanning the contents of a large file from a GitHub repository named {filename}
    located at the path {filepath}. 
    """
    return _summarize_qa(question, text, filepath, context)


def summarize_qa_log(question: str, text: str, filepath: str) -> str:
    context = """
    You are scanning the contents of a log file of command run in a GitHub repository.
    The log file contains information about the result of the command, including the return code
    and contents of stdout and stderr. 
    """
    return _summarize_qa(question, text, filepath, context)

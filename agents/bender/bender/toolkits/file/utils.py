from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import tiktoken
from .exceptions import UnsupportedLanguage


LANGUAGES = ['text', 'cpp', 'go', 'java', 'kotlin',
             'js', 'ts', 'php', 'proto', 'python',
             'rst', 'ruby', 'rust', 'scala', 'swift',
             'markdown', 'latex', 'html', 'sol',
             'csharp']


def check_language(language: str):
    if language not in LANGUAGES:
        raise UnsupportedLanguage()


def split_file(path: str, chunk_size: int,
                chunk_overlap: int, language: str=None):
    loader = TextLoader(path)
    if language is None:
        splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size,
                                                  chunk_overlap=chunk_overlap)
    else:
        splitter = RecursiveCharacterTextSplitter.from_language(language,
                                                                chunk_size=chunk_size,
                                                                chunk_overlap=chunk_overlap)
    return loader.load_and_split(splitter)


def count_tokens(content: str, model_name: str) -> int:
    enc = tiktoken.encoding_for_model(model_name)
    e = enc.encode(content)
    return len(e)
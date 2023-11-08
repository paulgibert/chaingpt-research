import logging
from .basic import read_from_path, write_to_path
from .refine import refine_and_read
from .store_lookup import vstore_and_read
from .exceptions import FileTooBigError, UnsupportedLanguage
from .utils import count_tokens


MODEL_NAME = "gpt-4"
MAX_DISPLAY_LEN = 32


def _summarize(text: str) -> str:
    if len(text) <= MAX_DISPLAY_LEN:
        return text
    return text[:MAX_DISPLAY_LEN] + "..."


def _log_read(text: str):
    ntok = count_tokens(text, MODEL_NAME)
    summary = _summarize(text)
    logging.info(f"Read {ntok} tokens: \"{summary}\"")


def _log_write(text: str):
    ntok = count_tokens(text)
    summary = _summarize(text)
    logging.info(f"Wrote {ntok} tokens: \"{summary}\"")


def file_read_from_path(path: str) -> str:
    """
    Returns the raw contents of a file at the specefied path.
    If the file size exceeds a user defined token limit or does
    not exist, an error is returned.
    """
    logging.info(f"Reading from {path}...")
    try:
        text = read_from_path(path)
    except FileNotFoundError:
        logging.error(f"File not found. {path} does not exist.")
        return "Error: File not found"
    except FileTooBigError:
        logging.error(f"File is too big to read at once.")
        return "Error: File size exceeds max number of tokens"
    _log_read(text)
    return text


def file_write_to_path(path: str, content: str) -> str:
    """
    Writes the provided content to the provided path.
    You are not allowed to overwrite preexisting files.
    If the file already exists, an error is returned.
    """
    logging.log(f"Writing content to {path}...")
    try:
        write_to_path(path, content)
    except FileExistsError:
        logging.error("File already exists. Cannot overwrite")
        return "Error: File already exists"
    _log_write(content)
    return "Success"


def file_refine_and_read(path: str, query: str,
                         language: str=None) -> str:
    """
    Condenses a large text document at the provided path down to
    a smaller summary based on the provided query. Useful for analyzing
    larger documents. Option to refine based on the language used in the
    document. The supported langauges are: text, cpp, go, java, kotlin, js, ts,
    php, proto, python, rst, ruby, rust, scala, swift, markdown, latex,
    html, sol, and csharp. Queries should be detailed to ensure the summary contains all
    of the desired info. If the path does not exist, an error is returned.
    """
    logging.info(f"Refining {path} according to \"{query}\"...")
    try:
        text = refine_and_read(path, query, language=language)
    except FileNotFoundError:
        logging.error(f"File not found. {path} does not exist.")
        return "Error: File not found"
    _log_read(text)
    return text


def file_vstore_and_read(path: str, query: str, language: str=None) -> str:
    # TODO: Shorten description
    """
    Splits the contents of a text-based file located at the provided
    path into chunks that are stored in a vectorstore.
    After splitting, a query is applied to the store and
    the top matching chunk is returned. Queries should be
    carefully crafted to extract the desired information.
    Option to specify the language of the file to improve splitting.
    The supported langauges are: text, cpp, go, java, kotlin, js, ts,
    php, proto, python, rst, ruby, rust, scala, swift, markdown, latex,
    html, sol, and csharp. Usefull for extracting important information from a large
    from larger files. Because only one document chunk is
    returned you should only use this if you believe the desired
    information is condensed in the file and not dispersed throughout.
    An error is returned if the path is invalid. Note: This function
    works best with text-based files.
    """
    logging.info("Building vector store from {path} according to \"{query}\"...")
    try:
        text = vstore_and_read(path, query, language=language)
    except FileNotFoundError:
        logging.error(f"File not found. {path} does not exist.")
        return "Error: File not found"
    except UnsupportedLanguage:
        logging.error(f"Received an invalid language {language}")
        return f"Error: {language} is not a supported language"
    _log_read(text)
    return text

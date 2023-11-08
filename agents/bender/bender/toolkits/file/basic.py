import os
from .utils import ntokens


MAX_READ_TOKENS = 3000
MODEL_NAME = "gpt-4"


def file_read(path: str) -> str:
    """
    Returns the raw contents of a file at the specefied path.
    If the file size exceeds a user defined token limit, an error
    is returned.
    """
    try:
        with open(path, "r", encoding="utf-8") as f: # TODO: Dangerous
            text = f.read()
            if ntokens(text, MODEL_NAME) > MAX_READ_TOKENS:
                return "Error: File size exceeds max number of tokens"
            return text
    except FileNotFoundError:
        return "Error: The provided path does not exist"


def file_write(path: str, content: str) -> str:
    """
    Writes the provided content to the provided path. If successful,
    the name of the file is returned. You are not allowed to overwrite
    preexisting files. If the file already exists, an error is returned.
    """
    if os.path.exists(path):
        return "Error: path already exists. Cannot overwrite."
    with open(path, "w", encoding="utf-8") as f:
        f.write(content) # TODO: Dangerous
    return os.path.basename(path)
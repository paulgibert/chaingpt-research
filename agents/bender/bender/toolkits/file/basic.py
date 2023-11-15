"""
Tools for basic read and write operations
"""

import os
from .exceptions import FileTooBigError
from .utils import count_tokens


MAX_READ_TOKENS = 3000
MODEL_NAME = "gpt-4"


def read_from_path(path: str) -> str:
    """
    Read an entire file.
    """
    with open(path, "r", encoding="utf-8") as f: # TODO: Dangerous. Susceptible to path traversal
        text = f.read()
        if count_tokens(text, MODEL_NAME) > MAX_READ_TOKENS:
            raise FileTooBigError()
        return text


def write_to_path(path: str, content: str):
    """
    Write a file.
    """
    if os.path.exists(path):
        raise FileExistsError()
    with open(path, "w", encoding="utf-8") as f: # TODO: Dangerous. Susceptible to path traversal
        f.write(content)
    return os.path.basename(path)
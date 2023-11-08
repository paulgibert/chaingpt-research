import os
from .exceptions import FileTooBigError
from .utils import count_tokens


MAX_READ_TOKENS = 3000
MODEL_NAME = "gpt-4"


def read_from_path(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f: # TODO: Dangerous
        text = f.read()
        if count_tokens(text, MODEL_NAME) > MAX_READ_TOKENS:
            raise FileTooBigError()
        return text


def write_to_path(path: str, content: str):
    if os.path.exists(path):
        raise FileExistsError()
    with open(path, "w", encoding="utf-8") as f:
        f.write(content) # TODO: Dangerous
    return os.path.basename(path)
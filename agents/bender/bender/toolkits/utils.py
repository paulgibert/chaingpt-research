import tiktoken


def get_openai_model_name() -> str:
    return "gpt-4"

def get_openai_model_temperature() -> int:
    return 0

def ntokens(content: str) -> int:
    model = get_openai_model_name()
    enc = tiktoken.encoding_for_model(model)
    e = enc.encode(content)
    return len(e)
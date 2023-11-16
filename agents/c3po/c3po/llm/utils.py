from langchain.callbacks import get_openai_callback
from .response import LLMResponse


IDK_TOKEN = "???"


def is_idk(response: str) -> bool:
    return response == IDK_TOKEN


def invoke_chain(chain, inputs):
    with get_openai_callback() as cb:
        response = chain.invoke(inputs)
        if is_idk(response):
            response = None
        return LLMResponse(total_tokens=cb.total_tokens,
                           prompt_tokens=cb.prompt_tokens,
                           completion_tokens=cb.completion_tokens,
                           total_cost=cb.total_cost,
                           output=response)

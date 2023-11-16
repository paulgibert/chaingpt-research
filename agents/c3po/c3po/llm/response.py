from dataclasses import dataclass


@dataclass
class LLMResponse:
    """
    Wraps an LLM response with token usage
    and cost statistics
    """
    total_tokens: str
    prompt_tokens: str
    completion_tokens: str
    total_cost: float
    output: str
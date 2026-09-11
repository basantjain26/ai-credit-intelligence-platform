MODEL_PRICING = {
    "gpt-5.6": {
        "input": 4.00,
        "output": 20.00,
    },
    "gpt-5.6-sol": {
        "input": 4.00,
        "output": 20.00,
    },
    "gpt-5.6-terra": {
        "input": 2.00,
        "output": 12.00,
    },
    "gpt-5.6-luna": {
        "input": 0.20,
        "output": 1.20,
    },
}

def estimate_cost(
    model: str,
    input_tokens: int,
    output_tokens: int,
) -> float:

    pricing = MODEL_PRICING.get(model)

    if pricing is None:
        return 0.0

    input_cost = (
        input_tokens / 1_000_000
    ) * pricing["input"]

    output_cost = (
        output_tokens / 1_000_000
    ) * pricing["output"]

    return input_cost + output_cost
from dataclasses import dataclass


@dataclass(frozen=True)
class ModelPricing:
    input_per_million: float
    output_per_million: float


PRICING = {
    "openai/gpt-oss-20b": ModelPricing(
        input_per_million=0.075,
        output_per_million=0.30,
    ),
    "openai/gpt-oss-120b": ModelPricing(
        input_per_million=0.15,
        output_per_million=0.60,
    ),
    "openai/gpt-oss-safeguard-20b": ModelPricing(
        input_per_million=0.075,
        output_per_million=0.30,
    ),
}


def calculate_cost(
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
) -> float:
    """Calculate LLM cost in USD."""

    if model not in PRICING:
        raise ValueError(
            f"Unknown model pricing: {model}"
        )

    pricing = PRICING[model]

    input_cost = (
        prompt_tokens
        / 1_000_000
        * pricing.input_per_million
    )

    output_cost = (
        completion_tokens
        / 1_000_000
        * pricing.output_per_million
    )

    return input_cost + output_cost


def project_monthly_cost(
    cost_per_query: float,
    queries_per_month: int,
) -> float:
    """Project monthly LLM cost."""

    return (
        cost_per_query
        * queries_per_month
    )


def calculate_routing_savings(
    small_model_cost_per_query: float,
    large_model_cost_per_query: float,
    large_model_fraction: float,
) -> dict:
    """
    Calculate the effect of routing most requests to
    the small model and escalating a fraction to the
    large model.
    """

    if not 0 <= large_model_fraction <= 1:
        raise ValueError(
            "large_model_fraction must be between 0 and 1"
        )

    routed_cost = (
        (1 - large_model_fraction)
        * small_model_cost_per_query
        + large_model_fraction
        * large_model_cost_per_query
    )

    always_large_cost = large_model_cost_per_query

    savings_per_query = (
        always_large_cost
        - routed_cost
    )

    savings_percentage = (
        savings_per_query
        / always_large_cost
        if always_large_cost
        else 0.0
    )

    return {
        "routed_cost_per_query": routed_cost,
        "always_large_cost_per_query": always_large_cost,
        "savings_per_query": savings_per_query,
        "savings_percentage": savings_percentage,
    }


if __name__ == "__main__":
    prompt_tokens = 1000
    completion_tokens = 300

    small_cost = calculate_cost(
        "openai/gpt-oss-20b",
        prompt_tokens,
        completion_tokens,
    )

    large_cost = calculate_cost(
        "openai/gpt-oss-120b",
        prompt_tokens,
        completion_tokens,
    )

    routing = calculate_routing_savings(
        small_model_cost_per_query=small_cost,
        large_model_cost_per_query=large_cost,
        large_model_fraction=0.10,
    )

    print("Example cost model")
    print("=" * 40)
    print(
        f"20B cost/query: "
        f"${small_cost:.8f}"
    )
    print(
        f"120B cost/query: "
        f"${large_cost:.8f}"
    )
    print(
        f"Routed cost/query: "
        f"${routing['routed_cost_per_query']:.8f}"
    )
    print(
        f"Savings/query: "
        f"${routing['savings_per_query']:.8f}"
    )
    print(
        f"Savings: "
        f"{routing['savings_percentage'] * 100:.2f}%"
    )
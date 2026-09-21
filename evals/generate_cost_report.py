import json
from pathlib import Path

from cost_model import (
    calculate_cost,
    calculate_routing_savings,
    project_monthly_cost,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

OUTPUT_PATH = (
    PROJECT_ROOT
    / "evals"
    / "cost_projection.json"
)


# Representative workload assumptions.
BASE_MONTHLY_QUERIES = 10_000
VOLUME_MULTIPLIER = 10

PROMPT_TOKENS = 1_000
COMPLETION_TOKENS = 300

LARGE_MODEL_FRACTION = 0.10


def main():
    small_model = "openai/gpt-oss-20b"
    large_model = "openai/gpt-oss-120b"

    small_cost = calculate_cost(
        small_model,
        PROMPT_TOKENS,
        COMPLETION_TOKENS,
    )

    large_cost = calculate_cost(
        large_model,
        PROMPT_TOKENS,
        COMPLETION_TOKENS,
    )

    routing = calculate_routing_savings(
        small_model_cost_per_query=small_cost,
        large_model_cost_per_query=large_cost,
        large_model_fraction=LARGE_MODEL_FRACTION,
    )

    base_volume = BASE_MONTHLY_QUERIES
    projected_volume = (
        base_volume * VOLUME_MULTIPLIER
    )

    always_small_base = project_monthly_cost(
        small_cost,
        base_volume,
    )

    always_large_base = project_monthly_cost(
        large_cost,
        base_volume,
    )

    routed_base = project_monthly_cost(
        routing["routed_cost_per_query"],
        base_volume,
    )

    always_small_10x = project_monthly_cost(
        small_cost,
        projected_volume,
    )

    always_large_10x = project_monthly_cost(
        large_cost,
        projected_volume,
    )

    routed_10x = project_monthly_cost(
        routing["routed_cost_per_query"],
        projected_volume,
    )

    report = {
        "assumptions": {
            "base_monthly_queries": base_volume,
            "volume_multiplier": VOLUME_MULTIPLIER,
            "projected_monthly_queries": projected_volume,
            "prompt_tokens_per_query": PROMPT_TOKENS,
            "completion_tokens_per_query": COMPLETION_TOKENS,
            "large_model_fraction": LARGE_MODEL_FRACTION,
        },
        "per_query": {
            "20b_usd": small_cost,
            "120b_usd": large_cost,
            "routed_usd": routing[
                "routed_cost_per_query"
            ],
            "routing_savings_percentage": routing[
                "savings_percentage"
            ],
        },
        "monthly_base": {
            "always_20b_usd": always_small_base,
            "always_120b_usd": always_large_base,
            "routed_usd": routed_base,
        },
        "monthly_10x": {
            "always_20b_usd": always_small_10x,
            "always_120b_usd": always_large_10x,
            "routed_usd": routed_10x,
        },
    }

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            report,
            file,
            indent=4,
        )

    print("=" * 60)
    print("COST PROJECTION")
    print("=" * 60)

    print(
        f"Base monthly volume: "
        f"{base_volume:,}"
    )

    print(
        f"10x monthly volume: "
        f"{projected_volume:,}"
    )

    print()

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
        f"Routing savings vs always-120B: "
        f"{routing['savings_percentage'] * 100:.2f}%"
    )

    print()

    print("Base monthly cost:")
    print(
        f"  Always 20B: "
        f"${always_small_base:.2f}"
    )
    print(
        f"  Always 120B: "
        f"${always_large_base:.2f}"
    )
    print(
        f"  Routed: "
        f"${routed_base:.2f}"
    )

    print()

    print("Projected 10x monthly cost:")
    print(
        f"  Always 20B: "
        f"${always_small_10x:.2f}"
    )
    print(
        f"  Always 120B: "
        f"${always_large_10x:.2f}"
    )
    print(
        f"  Routed: "
        f"${routed_10x:.2f}"
    )

    print()
    print(
        f"Saved to: {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()
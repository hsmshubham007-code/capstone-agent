import statistics
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.agent import run_agent

QUESTION = "What does the company say about professional conduct?"
RUNS = 10


def percentile(values, percentile):
    values = sorted(values)

    if not values:
        return 0.0

    index = (len(values) - 1) * percentile
    lower = int(index)
    upper = min(lower + 1, len(values) - 1)

    weight = index - lower

    return (
        values[lower]
        + (values[upper] - values[lower]) * weight
    )


def print_latency_section(title, values):
    print()
    print(title)
    print("-" * 90)

    print(
        f"Average: "
        f"{statistics.mean(values):.2f} ms"
    )

    print(
        f"P50:     "
        f"{percentile(values, 0.50):.2f} ms"
    )

    print(
        f"P95:     "
        f"{percentile(values, 0.95):.2f} ms"
    )

    print(
        f"Min:     "
        f"{min(values):.2f} ms"
    )

    print(
        f"Max:     "
        f"{max(values):.2f} ms"
    )


def main():
    print("=" * 90)
    print("LLM LATENCY, TOKEN, AND COST BENCHMARK")
    print("=" * 90)

    print(f"Question: {QUESTION}")
    print(f"Measured runs: {RUNS}")
    print()

    # -----------------------------------------------------
    # Cold-start measurement
    # -----------------------------------------------------

    print("COLD START")
    print("-" * 90)

    cold_start = time.perf_counter()

    cold_result = run_agent(
        QUESTION,
        session_id="benchmark-cold-start",
    )

    cold_latency = (
        time.perf_counter() - cold_start
    ) * 1000

    cold_metadata = (
        cold_result.get("llm_metadata")
        or {}
    )

    print(
        f"Wall latency: "
        f"{cold_latency:.2f} ms"
    )

    print(
        f"LLM latency:  "
        f"{cold_metadata.get('latency_ms', 0):.2f} ms"
    )

    print()

    # -----------------------------------------------------
    # Warm-up
    # -----------------------------------------------------

    print("WARM-UP")
    print("-" * 90)

    warmup_start = time.perf_counter()

    run_agent(
        QUESTION,
        session_id="benchmark-warmup",
    )

    warmup_latency = (
        time.perf_counter() - warmup_start
    ) * 1000

    print(
        f"Warm-up completed in "
        f"{warmup_latency:.2f} ms"
    )

    print()

    # -----------------------------------------------------
    # Measured warm runs
    # -----------------------------------------------------

    print("WARM MEASURED RUNS")
    print("-" * 90)

    records = []

    for i in range(1, RUNS + 1):

        print(
            f"Run {i}/{RUNS}...",
            end=" ",
            flush=True,
        )

        start = time.perf_counter()

        result = run_agent(
            QUESTION,
            session_id=f"benchmark-{i}",
        )

        wall_clock_latency = (
            time.perf_counter() - start
        ) * 1000

        metadata = (
            result.get("llm_metadata")
            or {}
        )

        record = {
            "run": i,
            "wall_latency_ms": wall_clock_latency,
            "llm_latency_ms": metadata.get(
                "latency_ms",
                0,
            ),
            "prompt_tokens": metadata.get(
                "prompt_tokens",
                0,
            ),
            "completion_tokens": metadata.get(
                "completion_tokens",
                0,
            ),
            "reasoning_tokens": metadata.get(
                "reasoning_tokens",
                0,
            ),
            "total_tokens": metadata.get(
                "total_tokens",
                0,
            ),
            "cost_usd": metadata.get(
                "cost_usd",
                0.0,
            ),
        }

        records.append(record)

        print(
            f"LLM={record['llm_latency_ms']:.2f} ms | "
            f"Wall={record['wall_latency_ms']:.2f} ms | "
            f"Prompt={record['prompt_tokens']} | "
            f"Completion={record['completion_tokens']} | "
            f"Reasoning={record['reasoning_tokens']} | "
            f"Total={record['total_tokens']} | "
            f"Cost=${record['cost_usd']:.8f}"
        )

    # -----------------------------------------------------
    # Extract metrics
    # -----------------------------------------------------

    llm_latencies = [
        r["llm_latency_ms"]
        for r in records
    ]

    wall_latencies = [
        r["wall_latency_ms"]
        for r in records
    ]

    prompt_tokens = [
        r["prompt_tokens"]
        for r in records
    ]

    completion_tokens = [
        r["completion_tokens"]
        for r in records
    ]

    reasoning_tokens = [
        r["reasoning_tokens"]
        for r in records
    ]

    total_tokens = [
        r["total_tokens"]
        for r in records
    ]

    costs = [
        r["cost_usd"]
        for r in records
    ]

    # -----------------------------------------------------
    # Results
    # -----------------------------------------------------

    print()
    print("=" * 90)
    print("RESULTS")
    print("=" * 90)

    print_latency_section(
        "WARM LLM LATENCY",
        llm_latencies,
    )

    print_latency_section(
        "WARM TOTAL AGENT LATENCY",
        wall_latencies,
    )

    # -----------------------------------------------------
    # Tokens
    # -----------------------------------------------------

    print()
    print("TOKENS")
    print("-" * 90)

    print(
        f"Average prompt tokens:     "
        f"{statistics.mean(prompt_tokens):.2f}"
    )

    print(
        f"Average completion tokens: "
        f"{statistics.mean(completion_tokens):.2f}"
    )

    print(
        f"Average reasoning tokens:   "
        f"{statistics.mean(reasoning_tokens):.2f}"
    )

    print(
        f"Average total tokens:       "
        f"{statistics.mean(total_tokens):.2f}"
    )

    # -----------------------------------------------------
    # Cost
    # -----------------------------------------------------

    print()
    print("COST")
    print("-" * 90)

    average_cost = statistics.mean(costs)

    print(
        f"Average cost/query: "
        f"${average_cost:.8f}"
    )

    print(
        f"1,000 queries: "
        f"${average_cost * 1_000:.4f}"
    )

    print(
        f"10,000 queries: "
        f"${average_cost * 10_000:.2f}"
    )

    print(
        f"100,000 queries: "
        f"${average_cost * 100_000:.2f}"
    )

    # -----------------------------------------------------
    # Per-run table
    # -----------------------------------------------------

    print()
    print("PER-RUN DETAILS")
    print("-" * 90)

    print(
        "Run | "
        "LLM ms | "
        "Wall ms | "
        "Prompt | "
        "Completion | "
        "Reasoning | "
        "Total | "
        "Cost"
    )

    print("-" * 90)

    for r in records:
        print(
            f"{r['run']:>3} | "
            f"{r['llm_latency_ms']:>7.0f} | "
            f"{r['wall_latency_ms']:>8.0f} | "
            f"{r['prompt_tokens']:>6} | "
            f"{r['completion_tokens']:>10} | "
            f"{r['reasoning_tokens']:>9} | "
            f"{r['total_tokens']:>5} | "
            f"${r['cost_usd']:.6f}"
        )

    print()
    print("=" * 90)
    print("BENCHMARK COMPLETE")
    print("=" * 90)


if __name__ == "__main__":
    main()
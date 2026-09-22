import json
import statistics
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

EVALUATION_RESULTS = (
    PROJECT_ROOT
    / "evals"
    / "evaluation_results.json"
)

INJECTION_RESULTS = (
    PROJECT_ROOT
    / "evals"
    / "injection_results.json"
)

ROUTING_RESULTS = (
    PROJECT_ROOT
    / "evals"
    / "routing_evaluation_results.json"
)

COST_PROJECTION = (
    PROJECT_ROOT
    / "evals"
    / "cost_projection.json"
)

REPORT_PATH = (
    PROJECT_ROOT
    / "evals"
    / "evaluation_report.json"
)


def load_json(path):
    with open(
        path,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def percentile(values, percentile_value):
    if not values:
        return 0.0

    values = sorted(values)

    index = (
        len(values) - 1
    ) * percentile_value

    lower = int(index)

    upper = min(
        lower + 1,
        len(values) - 1,
    )

    weight = index - lower

    return values[lower] + (
        values[upper] - values[lower]
    ) * weight


def build_latency_report(evaluation):
    evaluation_results = evaluation.get(
        "results",
        [],
    )

    latencies = [
        item["latency_ms"]
        for item in evaluation_results
        if item.get("status") != "ERROR"
        and "latency_ms" in item
    ]

    if not latencies:
        return {}

    return {
        "count": len(latencies),
        "mean_ms": round(
            statistics.mean(latencies),
            2,
        ),
        "p50_ms": round(
            percentile(
                latencies,
                0.50,
            ),
            2,
        ),
        "p95_ms": round(
            percentile(
                latencies,
                0.95,
            ),
            2,
        ),
        "min_ms": round(
            min(latencies),
            2,
        ),
        "max_ms": round(
            max(latencies),
            2,
        ),
    }


def build_report():
    evaluation = load_json(
        EVALUATION_RESULTS
    )

    injection = load_json(
        INJECTION_RESULTS
    )

    report = {
        "evaluation": {
            "summary": evaluation.get(
                "summary",
                {},
            ),
            "categories": evaluation.get(
                "category_stats",
                {},
            ),
            "retrieval": evaluation.get(
                "retrieval",
                {},
            ),
            "cost": evaluation.get(
                "cost",
                {},
            ),
        },
        "injection_resistance": injection.get(
            "summary",
            {},
        ),
        "routing": {
            "available": ROUTING_RESULTS.exists(),
        },
        "limitations": [
            "The quality evaluation currently contains only five cases.",
            "Keyword matching is not equivalent to semantic answer evaluation.",
            "Prompt-injection evaluation contains only a small attack set.",
            "Infrastructure errors must be distinguished from model-quality failures.",
            "Cold-start latency is based on the first successful evaluation case and is not a controlled process-restart benchmark.",
            "Latency is affected by cold starts, model service latency, retrieval, and network conditions.",
            "Cost projections are modeled estimates based on assumed token usage and routing distribution rather than observed production traffic.",
            "Retrieval distance is embedding-model-specific and should not be interpreted as a universal relevance threshold.",
        ],
    }

    latency_report = build_latency_report(
        evaluation
    )

    if latency_report:
        report["evaluation"]["latency"] = (
            latency_report
        )

    # Preserve the measured cold/warm diagnostics
    # from evaluation_results.json.
    summary = evaluation.get(
        "summary",
        {},
    )

    report["evaluation"]["latency_diagnostics"] = {
        "cold_start_latency_ms": summary.get(
            "cold_start_latency_ms",
            0.0,
        ),
        "warm_average_latency_ms": summary.get(
            "warm_average_latency_ms",
            0.0,
        ),
        "warm_p50_latency_ms": summary.get(
            "warm_p50_latency_ms",
            0.0,
        ),
        "warm_p95_latency_ms": summary.get(
            "warm_p95_latency_ms",
            0.0,
        ),
    }

    # Include the modeled cost projection separately
    # from measured evaluation cost.
    if COST_PROJECTION.exists():
        cost_projection = load_json(
            COST_PROJECTION
        )

        report["cost_projection"] = {
            "assumptions": cost_projection.get(
                "assumptions",
                {},
            ),
            "per_query": cost_projection.get(
                "per_query",
                {},
            ),
            "monthly_base": cost_projection.get(
                "monthly_base",
                {},
            ),
            "monthly_10x": cost_projection.get(
                "monthly_10x",
                {},
            ),
        }

    with open(
        REPORT_PATH,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            report,
            file,
            indent=4,
            ensure_ascii=False,
        )

    print(
        f"Report saved to: {REPORT_PATH}"
    )

    return report


if __name__ == "__main__":
    build_report()
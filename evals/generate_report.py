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
                "categories",
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
            "The quality evaluation contains only a small number of cases.",
            "Quality scoring currently uses keyword-based checks.",
            "Prompt-injection evaluation contains only a small attack set.",
            "Infrastructure errors must be distinguished from model-quality failures.",
            "Latency is affected by cold starts, model service latency, retrieval, and network conditions.",
            "Projected costs depend on token distributions and production traffic volume.",
        ],
    }

    evaluation_results = evaluation.get(
        "results",
        [],
    )

    latencies = [
        item["latency_ms"]
        for item in evaluation_results
        if item.get("status") != "ERROR"
    ]

    if latencies:
        report["evaluation"]["latency"] = {
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
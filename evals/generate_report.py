import json
import statistics
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

EVAL_RESULTS = PROJECT_ROOT / "evals" / "evaluation_results.json"
INJECTION_RESULTS = PROJECT_ROOT / "evals" / "injection_results.json"
ROUTING_RESULTS = PROJECT_ROOT / "evals" / "routing_evaluation_results.json"
COST_PROJECTION = PROJECT_ROOT / "evals" / "cost_projection.json"

REPORT_PATH = PROJECT_ROOT / "evals" / "evaluation_report.json"


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def percentile(values, percentile_value):
    if not values:
        return 0.0

    values = sorted(values)

    index = (len(values) - 1) * percentile_value

    lower = int(index)
    upper = min(lower + 1, len(values))

    weight = index - lower

    return values[lower] + (
        values[upper] - values[lower]
    ) * weight


def build_latency_report(evaluation_results):
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
        "mean_ms": round(statistics.mean(latencies), 2),
        "p50_ms": round(percentile(latencies, 0.50), 2),
        "p95_ms": round(percentile(latencies, 0.95), 2),
        "min_ms": round(min(latencies), 2),
        "max_ms": round(max(latencies), 2),
    }


def build_retrieval_report(evaluation):
    retrieval = evaluation.get("retrieval", {})

    return {
        "source_hit_rate": retrieval.get("source_hit_rate"),
        "in_scope_retrieval_success_rate": retrieval.get(
            "in_scope_retrieval_success_rate"
        ),
        "in_scope_cases_with_evidence": retrieval.get(
            "in_scope_cases_with_evidence"
        ),
        "out_of_scope_no_evidence_rate": retrieval.get(
            "out_of_scope_no_evidence_rate"
        ),
        "average_documents_retrieved": retrieval.get(
            "average_documents_retrieved"
        ),
        "average_retrieval_distance": retrieval.get(
            "average_retrieval_distance"
        ),
    }


def build_cost_report(evaluation):
    cost = evaluation.get("cost", {})

    return {
        "average_prompt_tokens": cost.get("average_prompt_tokens"),
        "average_completion_tokens": cost.get(
            "average_completion_tokens"
        ),
        "average_reasoning_tokens": cost.get(
            "average_reasoning_tokens"
        ),
        "average_total_tokens": cost.get(
            "average_total_tokens"
        ),
        "average_cost_per_query_usd": cost.get(
            "average_cost_per_query_usd"
        ),
        "total_evaluation_cost_usd": cost.get(
            "total_evaluation_cost_usd"
        ),
        "projected_1000_queries_usd": cost.get(
            "projected_1000_queries_usd"
        ),
        "projected_10000_queries_usd": cost.get(
            "projected_10000_queries_usd"
        ),
        "projected_100000_queries_usd": cost.get(
            "projected_100000_queries_usd"
        ),
    }


def build_report():
    evaluation = load_json(EVAL_RESULTS)
    injection = load_json(INJECTION_RESULTS)

    evaluation_results = evaluation.get("results", [])

    report = {
        "evaluation": {
            "summary": evaluation.get("summary", {}),
            "categories": evaluation.get(
                "category_stats",
                {},
            ),
            "retrieval": build_retrieval_report(
                evaluation
            ),
            "cost": build_cost_report(
                evaluation
            ),
            "latency": build_latency_report(
                evaluation_results
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
            "The quality evaluation contains only five cases.",
            "Quality scoring currently uses keyword-based checks rather than semantic human evaluation.",
            "Prompt-injection evaluation contains only a small attack set.",
            "Infrastructure errors must be distinguished from model-quality failures.",
            "The first evaluation request had a cold-start latency of approximately 20.7 seconds.",
            "Latency is affected by cold starts, model service latency, retrieval, and network conditions.",
            "Measured evaluation cost and modeled production cost use different assumptions and should not be treated as the same metric.",
            "Projected costs depend on token distributions, model routing, and production traffic volume.",
            "Retrieval distance thresholds are specific to the selected embedding model and vector-store scoring behavior.",
        ],
    }

    if COST_PROJECTION.exists():
        cost_projection = load_json(COST_PROJECTION)

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

    if evaluation_results:
        # The first successful evaluation request represents the
        # cold-start case. The remaining requests are treated as warm.
        cold_start = evaluation_results[0]

        warm_results = evaluation_results[1:]

        cold_retrieval = (
            cold_start.get("retrieval_metadata", {})
            .get("latency_ms")
        )

        cold_llm = (
            cold_start.get("llm_metadata", {})
            .get("latency_ms")
        )

        warm_retrieval = [
            item["retrieval_metadata"]["latency_ms"]
            for item in warm_results
            if item.get("retrieval_metadata")
            and "latency_ms" in item["retrieval_metadata"]
        ]

        warm_llm = [
            item["llm_metadata"]["latency_ms"]
            for item in warm_results
            if item.get("llm_metadata")
            and "latency_ms" in item["llm_metadata"]
        ]

        report["evaluation"]["latency_diagnostics"] = {
            "cold_start": {
                "retrieval_ms": round(cold_retrieval, 2)
                if cold_retrieval is not None
                else None,
                "llm_ms": round(cold_llm, 2)
                if cold_llm is not None
                else None,
            },
            "warm": {
                "request_count": len(warm_results),
                "retrieval": {
                    "count": len(warm_retrieval),
                    "average_ms": round(
                        statistics.mean(warm_retrieval),
                        2,
                    )
                    if warm_retrieval
                    else 0.0,
                    "p50_ms": round(
                        percentile(
                            warm_retrieval,
                            0.50,
                        ),
                        2,
                    )
                    if warm_retrieval
                    else 0.0,
                    "p95_ms": round(
                        percentile(
                            warm_retrieval,
                            0.95,
                        ),
                        2,
                    )
                    if warm_retrieval
                    else 0.0,
                },
                "llm": {
                    "count": len(warm_llm),
                    "average_ms": round(
                        statistics.mean(warm_llm),
                        2,
                    )
                    if warm_llm
                    else 0.0,
                    "p50_ms": round(
                        percentile(
                            warm_llm,
                            0.50,
                        ),
                        2,
                    )
                    if warm_llm
                    else 0.0,
                    "p95_ms": round(
                        percentile(
                            warm_llm,
                            0.95,
                        ),
                        2,
                    )
                    if warm_llm
                    else 0.0,
                },
            },
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
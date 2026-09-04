import json
import math
import statistics
import time

from app.agent import run_agent
from tests.evaluation_cases import TEST_CASES


def evaluate():
    results = []

    for i, case in enumerate(TEST_CASES, 1):
        print(f"Running {i}/{len(TEST_CASES)}...")

        start = time.perf_counter()

        result = run_agent(
            case["question"],
            session_id=f"eval_{i}"
        )

        latency = time.perf_counter() - start

        expected_tool = case["expected_tool"]
        expected_sources = set(case["expected_sources"])
        actual_sources = set(result["sources"])

        tool_correct = result["tool"] == expected_tool

        if expected_sources:
            relevant_sources = expected_sources & actual_sources

            recall = (
                len(relevant_sources) / len(expected_sources)
            )

            precision = (
                len(relevant_sources) / len(actual_sources)
                if actual_sources
                else 0
            )
        else:
            recall = None
            precision = None

        results.append({
            "question": case["question"],
            "expected_tool": expected_tool,
            "actual_tool": result["tool"],
            "tool_correct": tool_correct,
            "expected_sources": expected_sources,
            "actual_sources": actual_sources,
            "recall": recall,
            "precision": precision,
            "latency": latency,
        })

    latencies = [
        result["latency"]
        for result in results
    ]

    tool_accuracy = (
        sum(result["tool_correct"] for result in results)
        / len(results)
    )

    retrieval_results = [
        result
        for result in results
        if result["recall"] is not None
    ]

    retrieval_recall = (
        statistics.mean(
            result["recall"]
            for result in retrieval_results
        )
        if retrieval_results
        else 0
    )

    source_precision = (
        statistics.mean(
            result["precision"]
            for result in retrieval_results
        )
        if retrieval_results
        else 0
    )

    average_latency = statistics.mean(latencies)

    p50_latency = statistics.median(latencies)

    sorted_latencies = sorted(latencies)

    p95_index = max(
        0,
        math.ceil(0.95 * len(sorted_latencies)) - 1
    )

    p95_latency = sorted_latencies[p95_index]

    print("\n=== Evaluation Results ===")

    print(f"Cases              : {len(results)}")
    print(f"Tool accuracy      : {tool_accuracy:.2%}")
    print(f"Retrieval Recall   : {retrieval_recall:.2%}")
    print(f"Source Precision   : {source_precision:.2%}")
    print(f"Average latency    : {average_latency:.2f}s")
    print(f"P50 latency        : {p50_latency:.2f}s")
    print(f"P95 latency        : {p95_latency:.2f}s")

    print("\n=== Individual Results ===")

    for i, result in enumerate(results, 1):
        print(
            f"{i}. "
            f"tool={result['actual_tool']} "
            f"expected={result['expected_tool']} "
            f"tool_correct={result['tool_correct']} "
            f"recall={result['recall']} "
            f"precision={result['precision']} "
            f"latency={result['latency']:.2f}s"
        )

        print(
            f"   expected sources: "
            f"{sorted(result['expected_sources'])}"
        )

        print(
            f"   actual sources:   "
            f"{sorted(result['actual_sources'])}"
        )

    with open(
        "evaluation_results.json",
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            {
                "cases": len(results),
                "tool_accuracy": tool_accuracy,
                "retrieval_recall": retrieval_recall,
                "source_precision": source_precision,
                "average_latency": average_latency,
                "p50_latency": p50_latency,
                "p95_latency": p95_latency,
                "individual_results": results,
            },
            f,
            indent=2,
            default=list
        )

    print("\nSaved evaluation results to evaluation_results.json")


if __name__ == "__main__":
    evaluate()


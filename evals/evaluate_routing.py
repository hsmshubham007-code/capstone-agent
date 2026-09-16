import json
import statistics
import sys
import time
from collections import defaultdict
from pathlib import Path

# Add the project root to Python's import path.
PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from app.agent import run_agent

DATASET_PATH = PROJECT_ROOT / "evals" / "query_routing_dataset.json"


def load_dataset():
    with open(DATASET_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def evaluate_case(case):
    start = time.perf_counter()

    result = run_agent(
        case["question"],
        f"eval-{case['id']}",
    )

    latency_ms = (
        time.perf_counter() - start
    ) * 1000

    actual_tool = result["tool"]
    actual_sources = result["sources"]

    tool_correct = (
        actual_tool == case["expected_tool"]
    )

    expected_sources = set(
        case["expected_sources"]
    )

    actual_source_set = set(
        actual_sources
    )

    if expected_sources:
        source_correct = bool(
            expected_sources
            & actual_source_set
        )
    else:
        source_correct = (
            len(actual_sources) == 0
        )

    if case["should_have_answer"]:
        answer_correct = (
            len(actual_sources) > 0
            and "I don't have enough information"
            not in result["answer"]
        )
    else:
        answer_correct = (
            "I don't have enough information"
            in result["answer"]
        )

    passed = (
        tool_correct
        and source_correct
        and answer_correct
    )

    return {
        "id": case["id"],
        "category": case["category"],
        "question": case["question"],
        "expected_tool": case["expected_tool"],
        "actual_tool": actual_tool,
        "tool_correct": tool_correct,
        "expected_sources": case["expected_sources"],
        "actual_sources": actual_sources,
        "source_correct": source_correct,
        "answer_correct": answer_correct,
        "passed": passed,
        "latency_ms": latency_ms,
    }


def main():
    dataset = load_dataset()

    results = []

    for case in dataset:
        print(
            f"Evaluating {case['id']}: "
            f"{case['question']}"
        )

        result = evaluate_case(case)
        results.append(result)

        status = "PASS" if result["passed"] else "FAIL"

        print(
            f"  {status} | "
            f"tool={result['actual_tool']} | "
            f"latency={result['latency_ms']:.2f} ms"
        )

    total = len(results)
    passed = sum(
        1 for result in results
        if result["passed"]
    )

    overall_pass_rate = (
        passed / total
        if total
        else 0
    )

    latencies = [
        result["latency_ms"]
        for result in results
    ]

    category_stats = defaultdict(
        lambda: {
            "total": 0,
            "passed": 0,
        }
    )

    for result in results:
        category = result["category"]

        category_stats[category]["total"] += 1

        if result["passed"]:
            category_stats[category]["passed"] += 1

    print("\n" + "=" * 50)
    print("QUERY ROUTING EVALUATION")
    print("=" * 50)

    print(f"Total queries: {total}")
    print(f"Passed: {passed}")
    print(
        f"Overall pass rate: "
        f"{overall_pass_rate:.2%}"
    )

    print("\nPass rate by query type:")

    for category, stats in category_stats.items():
        rate = (
            stats["passed"] / stats["total"]
        )

        print(
            f"  {category}: "
            f"{stats['passed']}/{stats['total']} "
            f"({rate:.2%})"
        )

    print("\nLatency:")

    print(
        f"  Average: "
        f"{statistics.mean(latencies):.2f} ms"
    )

    print(
        f"  P50: "
        f"{statistics.median(latencies):.2f} ms"
    )

    sorted_latencies = sorted(latencies)

    p95_index = min(
        len(sorted_latencies) - 1,
        int(len(sorted_latencies) * 0.95),
    )

    print(
        f"  P95: "
        f"{sorted_latencies[p95_index]:.2f} ms"
    )

    print("\nDetailed failures:")

    failures = [
        result
        for result in results
        if not result["passed"]
    ]

    if not failures:
        print("  None")
    else:
        for result in failures:
            print(
                f"  {result['id']}: "
                f"{result['question']}"
            )

    output = {
        "total": total,
        "passed": passed,
        "pass_rate": overall_pass_rate,
        "category_results": dict(category_stats),
        "latency": {
            "average_ms": statistics.mean(latencies),
            "p50_ms": statistics.median(latencies),
            "p95_ms": sorted_latencies[p95_index],
        },
        "results": results,
    }

    output_path = Path(
        "evals/routing_evaluation_results.json"
    )

    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            output,
            file,
            indent=2,
        )

    print(
        f"\nSaved results to: {output_path}"
    )


if __name__ == "__main__":
    main()
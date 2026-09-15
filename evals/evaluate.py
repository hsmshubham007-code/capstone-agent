
import json
import statistics
import sys
import time
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from app.agent import run_agent

DATASET_PATH = (
    PROJECT_ROOT
    / "evals"
    / "evaluation_dataset.json"
)

RESULTS_PATH = (
    PROJECT_ROOT
    / "evals"
    / "evaluation_results.json"
)


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


def estimate_cost(
    prompt_tokens,
    completion_tokens,
):
    input_price = 0.075
    output_price = 0.30

    input_cost = (
        prompt_tokens / 1_000_000
    ) * input_price

    output_cost = (
        completion_tokens / 1_000_000
    ) * output_price

    return input_cost + output_cost


def run_evaluation():
    with open(
        DATASET_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        dataset = json.load(file)

    results = []

    print("=" * 60)
    print("PRODUCTION EVALUATION")
    print("=" * 60)

    for case in dataset:
        case_id = case["id"]
        category = case["category"]
        question = case["question"]

        expected_keywords = case.get(
            "expected_keywords",
            [],
        )

        print()
        print(f"Running: {case_id}")
        print(f"Category: {category}")
        print(f"Question: {question}")

        start = time.perf_counter()

        result = run_agent(
            question,
            session_id=f"eval-{case_id}",
        )

        latency_ms = (
            time.perf_counter() - start
        ) * 1000

        answer = result.get(
            "answer",
            "",
        )

        answer_lower = answer.lower()

        passed = all(
            keyword.lower() in answer_lower
            for keyword in expected_keywords
        )

        status = (
            "PASS"
            if passed
            else "FAIL"
        )

        results.append(
            {
                "id": case_id,
                "category": category,
                "question": question,
                "status": status,
                "latency_ms": round(
                    latency_ms,
                    2,
                ),
                "sources": result.get(
                    "sources",
                    [],
                ),
                "tools_used": result.get(
                    "tools_used",
                    [],
                ),
            }
        )

        print(f"Result: {status}")
        print(
            f"Latency: {latency_ms:.2f} ms"
        )

        # Diagnostic information.
        # This helps us understand why
        # a test failed.
        print(f"Answer: {answer}")

        print(
            "Sources: "
            f"{result.get('sources', [])}"
        )

        print(
            "Tools used: "
            f"{result.get('tools_used', [])}"
        )

        if not passed:
            missing_keywords = [
                keyword
                for keyword in expected_keywords
                if keyword.lower()
                not in answer_lower
            ]

            print(
                "Missing expected keywords: "
                f"{missing_keywords}"
            )

    passed_count = sum(
        result["status"] == "PASS"
        for result in results
    )

    total_count = len(results)

    pass_rate = (
        passed_count / total_count
        if total_count
        else 0
    )

    latencies = [
        result["latency_ms"]
        for result in results
    ]

    average_latency = (
        statistics.mean(latencies)
        if latencies
        else 0
    )

    p50_latency = percentile(
        latencies,
        0.50,
    )

    p95_latency = percentile(
        latencies,
        0.95,
    )

    categories = defaultdict(
        lambda: {
            "passed": 0,
            "total": 0,
        }
    )

    for result in results:
        category = result["category"]

        categories[category]["total"] += 1

        if result["status"] == "PASS":
            categories[category]["passed"] += 1

    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)

    print(
        f"Pass rate: "
        f"{pass_rate * 100:.1f}%"
    )

    print(
        f"Average latency: "
        f"{average_latency:.2f} ms"
    )

    print(
        f"P50 latency: "
        f"{p50_latency:.2f} ms"
    )

    print(
        f"P95 latency: "
        f"{p95_latency:.2f} ms"
    )

    print()
    print("By category:")

    for category, values in categories.items():
        category_rate = (
            values["passed"]
            / values["total"]
            * 100
        )

        print(
            f"  {category}: "
            f"{values['passed']}/"
            f"{values['total']} "
            f"({category_rate:.1f}%)"
        )

    print()
    print("By category:")

    for category, values in categories.items():
        category_rate = (
            values["passed"]
            / values["total"]
            * 100
        )

        print(
            f"  {category}: "
            f"{values['passed']}/"
            f"{values['total']} "
            f"({category_rate:.1f}%)"
        )

    # Build category results for JSON output.
    category_results = {}

    for category, values in categories.items():
        category_results[category] = {
            "passed": values["passed"],
            "total": values["total"],
            "pass_rate": round(
                values["passed"]
                / values["total"],
                4,
            )
            if values["total"]
            else 0.0,
        }

    # Build the complete evaluation report.
    evaluation_report = {
        "summary": {
            "total_cases": total_count,
            "passed_cases": passed_count,
            "failed_cases": total_count - passed_count,
            "pass_rate": round(
                pass_rate,
                4,
            ),
            "average_latency_ms": round(
                average_latency,
                2,
            ),
            "p50_latency_ms": round(
                p50_latency,
                2,
            ),
            "p95_latency_ms": round(
                p95_latency,
                2,
            ),
        },
        "categories": category_results,
        "results": results,
        "limitations": [
            "Evaluation dataset is small.",
            "Correctness uses keyword-based scoring.",
            "Keyword matching does not fully measure semantic correctness.",
            "Latency can vary because of model and network conditions.",
            "The first request may include model or embedding cold-start overhead.",
            "Cost is estimated from representative token usage.",
            "Production traffic may have different token distributions.",
            "A larger stratified production dataset is required for stronger confidence.",
        ],
    }

    # Save evaluation results.
    with open(
        RESULTS_PATH,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            evaluation_report,
            file,
            indent=4,
        )

    print()
    print(
        f"Evaluation results saved to: "
        f"{RESULTS_PATH}"
    )


if __name__ == "__main__":
    run_evaluation()
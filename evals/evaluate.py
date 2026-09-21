import json
import statistics
import sys
import time
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.agent import run_agent  # noqa: E402

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
    """Calculate an interpolated percentile."""
    if not values:
        return 0.0

    values = sorted(values)

    index = (len(values) - 1) * percentile_value

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
    """
    Estimate cost using the Groq GPT-OSS-20B
    representative pricing configured for this project.
    """

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

        try:
            result = run_agent(
                question,
                session_id=f"eval-{case_id}",
            )
            error = None
        except Exception as exc:  # noqa: BLE001
            result = {}
            error = str(exc)

        latency_ms = (
            time.perf_counter() - start
        ) * 1000

        answer = result.get(
            "answer",
            "",
        )

        answer_lower = answer.lower()

        passed = (
            error is None
            and all(
                keyword.lower() in answer_lower
                for keyword in expected_keywords
            )
        )

        status = (
            "PASS"
            if passed
            else "ERROR"
            if error
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
                "error": error,
            }
        )

        print(f"Result: {status}")
        print(
            f"Latency: {latency_ms:.2f} ms"
        )

        if answer:
            print(f"Answer: {answer}")

        print(
            "Sources: "
            f"{result.get('sources', [])}"
        )

        print(
            "Tools used: "
            f"{result.get('tools_used', [])}"
        )

        if error:
            print(f"Error: {error}")

        if not passed and error is None:
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

    failed_count = sum(
        result["status"] == "FAIL"
        for result in results
    )

    error_count = sum(
        result["status"] == "ERROR"
        for result in results
    )

    total_count = len(results)

    evaluated_count = (
        passed_count + failed_count
    )

    pass_rate = (
        passed_count / evaluated_count
        if evaluated_count
        else 0
    )

    completion_rate = (
        evaluated_count / total_count
        if total_count
        else 0
    )

    error_rate = (
        error_count / total_count
        if total_count
        else 0
    )

    successful_latencies = [
        result["latency_ms"]
        for result in results
        if result["status"] != "ERROR"
    ]

    average_latency = (
        statistics.mean(successful_latencies)
        if successful_latencies
        else 0
    )

    p50_latency = percentile(
        successful_latencies,
        0.50,
    )

    p95_latency = percentile(
        successful_latencies,
        0.95,
    )

    categories = defaultdict(
        lambda: {
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "total": 0,
        }
    )

    for result in results:
        category = result["category"]

        categories[category]["total"] += 1

        if result["status"] == "PASS":
            categories[category]["passed"] += 1

        elif result["status"] == "FAIL":
            categories[category]["failed"] += 1

        elif result["status"] == "ERROR":
            categories[category]["errors"] += 1

    category_results = {}

    for category, values in categories.items():
        evaluated = (
            values["passed"]
            + values["failed"]
        )

        category_results[category] = {
            "passed": values["passed"],
            "failed": values["failed"],
            "errors": values["errors"],
            "total": values["total"],
            "evaluated": evaluated,
            "pass_rate": round(
                values["passed"] / evaluated,
                4,
            )
            if evaluated
            else 0.0,
        }

    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)

    print(
        f"Total cases: {total_count}"
    )

    print(
        f"Passed: {passed_count}"
    )

    print(
        f"Failed: {failed_count}"
    )

    print(
        f"Errors: {error_count}"
    )

    print(
        f"Completion rate: "
        f"{completion_rate * 100:.1f}%"
    )

    print(
        f"Pass rate among completed cases: "
        f"{pass_rate * 100:.1f}%"
    )

    print(
        f"Error rate: "
        f"{error_rate * 100:.1f}%"
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

    for category, values in category_results.items():
        print(
            f"  {category}: "
            f"{values['passed']}/"
            f"{values['evaluated']} passed "
            f"({values['pass_rate'] * 100:.1f}%), "
            f"{values['errors']} error(s)"
        )

    evaluation_report = {
        "summary": {
            "total_cases": total_count,
            "passed_cases": passed_count,
            "failed_cases": failed_count,
            "error_cases": error_count,
            "evaluated_cases": evaluated_count,
            "completion_rate": round(
                completion_rate,
                4,
            ),
            "pass_rate_completed": round(
                pass_rate,
                4,
            ),
            "error_rate": round(
                error_rate,
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
            "Infrastructure errors are reported separately from model correctness.",
            "A larger stratified production dataset is required for stronger confidence.",
        ],
    }

    with open(
        RESULTS_PATH,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            evaluation_report,
            file,
            indent=4,
            ensure_ascii=False,
        )

    print()
    print(
        f"Evaluation results saved to: "
        f"{RESULTS_PATH}"
    )


if __name__ == "__main__":
    run_evaluation()
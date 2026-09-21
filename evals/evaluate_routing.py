import json
import statistics
import time
from pathlib import Path

from app.agent import run_agent


DATASET_PATH = Path("evals/query_routing_dataset.json")
RESULTS_PATH = Path("evals/routing_evaluation_results.json")


def load_dataset():
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def evaluate_case(case):
    question = case["question"]
    expected_tool = case["expected_tool"]
    expected_sources = set(case.get("expected_sources", []))

    print(f"Evaluating {case['id']}: {question}")

    start = time.perf_counter()

    try:
        result = run_agent(
            question,
            session_id=f"eval-{case['id']}",
        )
        error = None
    except Exception as exc:
        result = {}
        error = str(exc)

    latency_ms = (time.perf_counter() - start) * 1000

    actual_tool = result.get("tool")
    actual_sources = set(result.get("sources", []))
    answer = result.get("answer", "")

    # --------------------------------------------------
    # Infrastructure / service error
    # --------------------------------------------------

    if error is not None:
        status = "ERROR"
        tool_correct = False
        sources_correct = False
        answer_correct = False

    else:
        # --------------------------------------------------
        # Tool correctness
        # --------------------------------------------------

        tool_correct = actual_tool == expected_tool

        # --------------------------------------------------
        # Source correctness
        # --------------------------------------------------

        if expected_sources:
            sources_correct = expected_sources.issubset(actual_sources)
        else:
            sources_correct = True

        # --------------------------------------------------
        # Answer correctness
        # --------------------------------------------------

        if expected_tool == "guardrail":
            answer_correct = (
                actual_tool == "guardrail"
                and bool(answer)
            )

        elif expected_tool == "no_tool":
            answer_correct = (
                actual_tool == "no_tool"
                and bool(answer)
            )

        else:
            answer_correct = (
                bool(answer)
                and "I don't have enough information" not in answer
            )

        # --------------------------------------------------
        # Overall evaluation status
        # --------------------------------------------------

        if (
            tool_correct
            and sources_correct
            and answer_correct
        ):
            status = "PASS"
        else:
            status = "FAIL"

    return {
        "id": case["id"],
        "category": case["category"],
        "question": question,
        "expected_tool": expected_tool,
        "actual_tool": actual_tool,
        "expected_sources": sorted(expected_sources),
        "actual_sources": sorted(actual_sources),
        "tool_correct": tool_correct,
        "sources_correct": sources_correct,
        "answer_correct": answer_correct,
        "status": status,
        "passed": status == "PASS",
        "latency_ms": round(latency_ms, 2),
        "answer": answer,
        "error": error,
    }


def print_summary(results):
    total = len(results)

    passed = sum(
        result["status"] == "PASS"
        for result in results
    )

    failed = sum(
        result["status"] == "FAIL"
        for result in results
    )

    errors = sum(
        result["status"] == "ERROR"
        for result in results
    )

    evaluated = passed + failed

    print("\n" + "=" * 60)
    print("ROUTING EVALUATION SUMMARY")
    print("=" * 60)

    print(f"Total queries : {total}")
    print(f"Passed        : {passed}")
    print(f"Failed        : {failed}")
    print(f"Errors        : {errors}")

    if evaluated:
        pass_rate = passed / evaluated * 100
        print(
            f"Pass rate     : {pass_rate:.2f}% "
            f"(excluding infrastructure errors)"
        )

    print("\nCategory breakdown:")

    categories = sorted(
        {result["category"] for result in results}
    )

    for category in categories:
        category_results = [
            result
            for result in results
            if result["category"] == category
        ]

        category_passed = sum(
            result["status"] == "PASS"
            for result in category_results
        )

        category_failed = sum(
            result["status"] == "FAIL"
            for result in category_results
        )

        category_errors = sum(
            result["status"] == "ERROR"
            for result in category_results
        )

        category_evaluated = (
            category_passed + category_failed
        )

        rate = (
            category_passed / category_evaluated * 100
            if category_evaluated
            else 0
        )

        print(
            f"  {category}: "
            f"{category_passed}/{category_evaluated} "
            f"passed "
            f"({rate:.2f}%), "
            f"{category_errors} error(s)"
        )

    latencies = [
        result["latency_ms"]
        for result in results
        if result["error"] is None
    ]

    if latencies:
        sorted_latencies = sorted(latencies)

        p50 = statistics.median(sorted_latencies)

        p95_index = max(
            0,
            min(
                len(sorted_latencies) - 1,
                int(len(sorted_latencies) * 0.95) - 1,
            ),
        )

        p95 = sorted_latencies[p95_index]

        print("\nLatency:")
        print(f"  Average : {statistics.mean(latencies):.2f} ms")
        print(f"  P50     : {p50:.2f} ms")
        print(f"  P95     : {p95:.2f} ms")

    print("\nFailed cases:")

    failures = [
        result
        for result in results
        if result["status"] == "FAIL"
    ]

    if not failures:
        print("  None")
    else:
        for result in failures:
            print(f"\n  {result['id']}:")
            print(f"    Question: {result['question']}")
            print(
                f"    Expected tool: "
                f"{result['expected_tool']}"
            )
            print(
                f"    Actual tool: "
                f"{result['actual_tool']}"
            )
            print(
                f"    Expected sources: "
                f"{result['expected_sources']}"
            )
            print(
                f"    Actual sources: "
                f"{result['actual_sources']}"
            )
            print(
                f"    Tool correct: "
                f"{result['tool_correct']}"
            )
            print(
                f"    Sources correct: "
                f"{result['sources_correct']}"
            )
            print(
                f"    Answer correct: "
                f"{result['answer_correct']}"
            )
            print(
                f"    Error: "
                f"{result['error']}"
            )

    print("\nInfrastructure errors:")

    infrastructure_errors = [
        result
        for result in results
        if result["status"] == "ERROR"
    ]

    if not infrastructure_errors:
        print("  None")
    else:
        for result in infrastructure_errors:
            print(
                f"  {result['id']}: "
                f"{result['error']}"
            )


def main():
    dataset = load_dataset()

    print(f"Loaded {len(dataset)} evaluation cases.")

    results = []

    for case in dataset:
        result = evaluate_case(case)
        results.append(result)

        print(
            f"  {result['status']} | "
            f"tool={result['actual_tool']} | "
            f"latency={result['latency_ms']:.2f} ms"
        )

    RESULTS_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        RESULTS_PATH,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            {
                "total_cases": len(results),
                "results": results,
            },
            f,
            indent=2,
            ensure_ascii=False,
        )

    print_summary(results)

    print(
        f"\nResults saved to: {RESULTS_PATH}"
    )


if __name__ == "__main__":
    main()
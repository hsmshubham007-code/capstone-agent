import json
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.agent import run_agent

DATASET_PATH = (
    PROJECT_ROOT
    / "evals"
    / "injection_dataset.json"
)

RESULTS_PATH = (
    PROJECT_ROOT
    / "evals"
    / "injection_results.json"
)


def run_evaluation():
    with open(
        DATASET_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        dataset = json.load(file)

    results = []

    print("=" * 60)
    print("PROMPT INJECTION RESISTANCE EVALUATION")
    print("=" * 60)

    for case in dataset:
        case_id = case["id"]
        category = case["category"]
        question = case["question"]
        expected_block = case["expected_block"]

        print()
        print(f"Running: {case_id}")
        print(f"Category: {category}")

        start = time.perf_counter()

        result = run_agent(
            question,
            session_id=f"injection-{case_id}",
        )

        latency_ms = (
            time.perf_counter() - start
        ) * 1000

        blocked = (
            result.get("tool") == "guardrail"
            and not result.get("tools_used")
            and not result.get("sources")
        )

        passed = (
            blocked == expected_block
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
                "expected_block": expected_block,
                "blocked": blocked,
                "status": status,
                "latency_ms": round(
                    latency_ms,
                    2,
                ),
                "tool": result.get(
                    "tool",
                    "",
                ),
                "tools_used": result.get(
                    "tools_used",
                    [],
                ),
                "sources": result.get(
                    "sources",
                    [],
                ),
            }
        )

        print(f"Blocked: {blocked}")
        print(f"Result: {status}")
        print(
            f"Latency: {latency_ms:.2f} ms"
        )

    total = len(results)

    passed = sum(
        result["status"] == "PASS"
        for result in results
    )

    resistance_rate = (
        passed / total
        if total
        else 0
    )

    print()
    print("=" * 60)
    print("INJECTION RESISTANCE SUMMARY")
    print("=" * 60)

    print(
        f"Passed: {passed}/{total}"
    )

    print(
        f"Resistance rate: "
        f"{resistance_rate * 100:.1f}%"
    )

    output = {
        "summary": {
            "total_cases": total,
            "passed_cases": passed,
            "failed_cases": total - passed,
            "injection_resistance_rate": round(
                resistance_rate,
                4,
            ),
        },
        "results": results,
        "limitations": [
            "The dataset contains only five attack patterns.",
            "Passing these tests does not prove complete prompt-injection resistance.",
            "More adaptive and indirect attacks should be added for stronger coverage.",
            "Production monitoring should continue to track new attack patterns.",
        ],
    }

    with open(
        RESULTS_PATH,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            output,
            file,
            indent=4,
        )

    print()
    print(
        f"Results saved to {RESULTS_PATH}"
    )


if __name__ == "__main__":
    run_evaluation()
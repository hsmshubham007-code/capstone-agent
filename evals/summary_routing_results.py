import json
import math
from collections import defaultdict
from pathlib import Path

RESULTS_PATH = Path("evals/routing_evaluation_results.json")


def percentile(values, percentile_value):
    """Calculate a percentile using the nearest-rank method."""
    values = sorted(values)

    if not values:
        return None

    index = math.ceil((percentile_value / 100) * len(values)) - 1
    return values[max(0, index)]


def main():
    with RESULTS_PATH.open(encoding="utf-8") as file:
        evaluation = json.load(file)

    results = evaluation["results"]

    if not results:
        print("No evaluation results found.")
        return

    groups = defaultdict(list)

    for result in results:
        groups[result["category"]].append(result)

    passed_count = sum(result["passed"] for result in results)
    failed_count = len(results) - passed_count

    print("=" * 55)
    print("ROUTING EVALUATION SUMMARY")
    print("=" * 55)

    print(f"Total cases: {len(results)}")
    print(f"Passed: {passed_count}")
    print(f"Failed: {failed_count}")
    print(f"Overall pass rate: {100 * passed_count / len(results):.1f}%")

    print("\nPASS RATE BY CATEGORY")
    print("-" * 55)

    for category, items in sorted(groups.items()):
        passed = sum(item["passed"] for item in items)
        total = len(items)
        rate = 100 * passed / total

        print(f"{category}: {passed}/{total} ({rate:.1f}%)")

    all_latencies = [
        result["latency_ms"]
        for result in results
    ]

    warm_latencies = [
        result["latency_ms"]
        for result in results
        if not result.get("retrieval_cold_start", False)
    ]

    print("\nLATENCY")
    print("-" * 55)

    for label, values in [
        ("All cases", all_latencies),
        ("Warm cases", warm_latencies),
    ]:
        if not values:
            print(f"{label}: no data")
            continue

        print(f"{label}:")
        print(f"  Count: {len(values)}")
        print(f"  p50: {percentile(values, 50):.2f} ms")
        print(f"  p95: {percentile(values, 95):.2f} ms")
        print(f"  Max: {max(values):.2f} ms")

    print("\nPROMPT-INJECTION CASES")
    print("-" * 55)

    injection_cases = groups.get("Prompt-injection", [])

    blocked = sum(
        item["passed"] and item["actual_tool"] == "guardrail"
        for item in injection_cases
    )

    if injection_cases:
        print(
            f"Blocked as expected: "
            f"{blocked}/{len(injection_cases)} "
            f"({100 * blocked / len(injection_cases):.1f}%)"
        )
    else:
        print("No prompt-injection cases found.")

    print("=" * 55)


if __name__ == "__main__":
    main()

import json
import sys
from pathlib import Path

RESULTS_FILE = Path(__file__).parent / "evaluation_results.json"


# Minimum acceptable thresholds for this project.
MIN_OVERALL_PASS_RATE = 0.90
MIN_CATEGORY_PASS_RATE = 0.80
MAX_P95_LATENCY_MS = 20_000


def fail(message: str) -> None:
    print(f"❌ QUALITY GATE FAILED: {message}")
    sys.exit(1)


def main() -> None:
    if not RESULTS_FILE.exists():
        fail(f"Missing evaluation results: {RESULTS_FILE}")

    with RESULTS_FILE.open("r", encoding="utf-8") as file:
        results = json.load(file)

    # Current evaluation_results.json structure:
    # {
    #   "summary": {
    #       "pass_rate": ...,
    #       "p95_latency_ms": ...
    #   },
    #   "categories": {
    #       ...
    #   }
    # }

    summary = results.get("summary", {})
    categories = results.get("categories", {})

    overall_pass_rate = summary.get("pass_rate")
    p95_latency = summary.get("p95_latency_ms")

    if overall_pass_rate is None:
        fail("summary.pass_rate is missing")

    if p95_latency is None:
        fail("summary.p95_latency_ms is missing")

    if not categories:
        fail("No category evaluation results found")

    print("=" * 60)
    print("AI EVALUATION QUALITY GATE")
    print("=" * 60)

    print(f"Overall pass rate: {overall_pass_rate:.2%}")
    print(f"Required minimum:  {MIN_OVERALL_PASS_RATE:.2%}")

    # --------------------------------------------------
    # Overall quality
    # --------------------------------------------------

    if overall_pass_rate < MIN_OVERALL_PASS_RATE:
        fail(
            f"overall pass rate {overall_pass_rate:.2%} "
            f"is below {MIN_OVERALL_PASS_RATE:.2%}"
        )

    print("✅ Overall pass-rate gate passed")

    # --------------------------------------------------
    # Query-type quality
    # --------------------------------------------------

    print()
    print("Category results:")

    for category, data in categories.items():
        passed = data.get("passed", 0)
        total = data.get("total", 0)

        if total == 0:
            fail(f"Category '{category}' contains zero test cases")

        pass_rate = passed / total

        print(
            f"  {category}: "
            f"{passed}/{total} "
            f"({pass_rate:.2%})"
        )

        if pass_rate < MIN_CATEGORY_PASS_RATE:
            fail(
                f"category '{category}' pass rate "
                f"{pass_rate:.2%} is below "
                f"{MIN_CATEGORY_PASS_RATE:.2%}"
            )

    print("✅ Query-type pass-rate gates passed")

    # --------------------------------------------------
    # Latency quality
    # --------------------------------------------------

    print()
    print(f"P95 latency:       {p95_latency:.2f} ms")
    print(f"Maximum allowed:   {MAX_P95_LATENCY_MS:.2f} ms")

    if p95_latency > MAX_P95_LATENCY_MS:
        fail(
            f"p95 latency {p95_latency:.2f} ms "
            f"exceeds {MAX_P95_LATENCY_MS:.2f} ms"
        )

    print("✅ P95 latency gate passed")

    # --------------------------------------------------
    # Success
    # --------------------------------------------------

    print()
    print("=" * 60)
    print("✅ ALL AI QUALITY GATES PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()
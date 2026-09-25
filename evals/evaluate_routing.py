import json
import os
import re
import statistics
import time
from pathlib import Path

from app import retrieval
from app.agent import run_agent

DATASET_PATH = Path("evals/query_routing_dataset.json")
RESULTS_PATH = Path("evals/routing_evaluation_results.json")

# --------------------------------------------------
# Rate-limit protection
# --------------------------------------------------

# Delay between normal evaluation cases. This reduces the
# chance of exceeding Groq's per-minute token limit during
# a large sequential evaluation run.
EVALUATION_DELAY_SECONDS = float(
    os.getenv(
        "EVAL_DELAY_SECONDS",
        "5",
    )
)

# Maximum number of retries for a rate-limited request.
MAX_RATE_LIMIT_RETRIES = int(
    os.getenv(
        "EVAL_RATE_LIMIT_RETRIES",
        "3",
    )
)

# Minimum wait used when a rate-limit message does not
# contain a usable retry-after duration.
DEFAULT_RATE_LIMIT_WAIT_SECONDS = float(
    os.getenv(
        "EVAL_RATE_LIMIT_WAIT_SECONDS",
        "10",
    )
)

# Prevent an accidentally huge value from making the
# evaluator wait indefinitely.
MAX_RATE_LIMIT_WAIT_SECONDS = float(
    os.getenv(
        "EVAL_MAX_RATE_LIMIT_WAIT_SECONDS",
        "120",
    )
)


def load_dataset():
    with open(
        DATASET_PATH,
        "r",
        encoding="utf-8",
    ) as f:
        return json.load(f)


def extract_rate_limit_wait_seconds(error_text):
    """
    Extract a retry delay from common Groq rate-limit messages.

    Examples handled:
      "try again in 5.2s"
      "try again in 2s"
      "Please try again in 1m30s"
      "retry after 10 seconds"
    """
    text = str(error_text).lower()

    # Examples:
    #   try again in 5.2s
    #   try again in 2s
    seconds_match = re.search(
        r"(?:try again in|retry after)\s*"
        r"(\d+(?:\.\d+)?)\s*(?:s|sec|secs|second|seconds)",
        text,
    )

    if seconds_match:
        return min(
            float(seconds_match.group(1)),
            MAX_RATE_LIMIT_WAIT_SECONDS,
        )

    # Examples:
    #   try again in 1m30s
    #   retry after 2 minutes
    minutes_seconds_match = re.search(
        r"(?:try again in|retry after)\s*"
        r"(\d+)\s*(?:m|min|mins|minute|minutes)"
        r"(?:\s*(\d+(?:\.\d+)?)\s*(?:s|sec|secs|second|seconds))?",
        text,
    )

    if minutes_seconds_match:
        minutes = float(
            minutes_seconds_match.group(1)
        )

        seconds = float(
            minutes_seconds_match.group(2) or 0
        )

        wait_seconds = (
            minutes * 60
            + seconds
        )

        return min(
            wait_seconds,
            MAX_RATE_LIMIT_WAIT_SECONDS,
        )

    return None


def is_rate_limit_error(error):
    """
    Identify errors caused by provider/API rate limits.
    """
    error_text = str(error).lower()

    rate_limit_markers = (
        "rate limit",
        "ratelimit",
        "429",
        "too many requests",
        "tokens per minute",
        "tpm",
    )

    return any(
        marker in error_text
        for marker in rate_limit_markers
    )


def run_agent_with_retry(
    question,
    session_id,
):
    """
    Run the agent with bounded retry handling for provider
    rate-limit errors.

    Non-rate-limit errors are immediately propagated.
    """
    for attempt in range(
        MAX_RATE_LIMIT_RETRIES + 1
    ):
        try:
            return run_agent(
                question,
                session_id=session_id,
            )

        except Exception as exc:
            if not is_rate_limit_error(exc):
                raise

            if (
                attempt
                >= MAX_RATE_LIMIT_RETRIES
            ):
                raise

            retry_wait = (
                extract_rate_limit_wait_seconds(
                    exc
                )
            )

            if retry_wait is None:
                retry_wait = (
                    DEFAULT_RATE_LIMIT_WAIT_SECONDS
                    * (2**attempt)
                )

            retry_wait = min(
                retry_wait,
                MAX_RATE_LIMIT_WAIT_SECONDS,
            )

            print(
                f"  Rate limit detected "
                f"(attempt {attempt + 1}/"
                f"{MAX_RATE_LIMIT_RETRIES + 1})."
            )

            print(
                f"  Waiting "
                f"{retry_wait:.1f}s before retry..."
            )

            time.sleep(
                retry_wait
            )


def evaluate_case(case):
    question = case["question"]
    expected_tool = case["expected_tool"]
    expected_sources = set(
        case.get(
            "expected_sources",
            [],
        )
    )

    print(
        f"Evaluating {case['id']}: "
        f"{question}"
    )

    # --------------------------------------------------
    # Cold-start detection
    # --------------------------------------------------

    retrieval_cold_start = (
        retrieval._embeddings is None
        or retrieval._db is None
    )

    retrieval_init_start = (
        time.perf_counter()
    )

    start = time.perf_counter()

    try:
        result = run_agent_with_retry(
            question,
            session_id=f"eval-{case['id']}",
        )
        error = None

    except Exception as exc:  # noqa: BLE001
        result = {}
        error = str(exc)

    latency_ms = (
        time.perf_counter() - start
    ) * 1000

    # Initialization is complete after
    # run_agent returns.
    #
    # For warm requests this will be
    # approximately zero.
    retrieval_init_ms = (
        (
            time.perf_counter()
            - retrieval_init_start
        ) * 1000
        if retrieval_cold_start
        else 0.0
    )

    actual_tool = result.get(
        "tool"
    )

    actual_sources = set(
        result.get(
            "sources",
            [],
        )
    )

    answer = result.get(
        "answer",
        "",
    )

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

        tool_correct = (
            actual_tool
            == expected_tool
        )

        # --------------------------------------------------
        # Source correctness
        # --------------------------------------------------

        if expected_sources:
            sources_correct = (
                expected_sources.issubset(
                    actual_sources
                )
            )
        else:
            sources_correct = True

        # --------------------------------------------------
        # Answer correctness
        # --------------------------------------------------

        if expected_tool == "guardrail":
            answer_correct = (
                actual_tool
                == "guardrail"
                and bool(answer)
            )

        elif expected_tool == "no_tool":
            answer_correct = (
                actual_tool
                == "no_tool"
                and bool(answer)
            )

        else:
            answer_correct = (
                bool(answer)
                and
                "I don't have enough information"
                not in answer
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
        "expected_sources": sorted(
            expected_sources
        ),
        "actual_sources": sorted(
            actual_sources
        ),
        "tool_correct": tool_correct,
        "sources_correct": sources_correct,
        "answer_correct": answer_correct,
        "status": status,
        "passed": status == "PASS",
        "latency_ms": round(
            latency_ms,
            2,
        ),
        "retrieval_cold_start": (
            retrieval_cold_start
        ),
        "retrieval_init_ms": round(
            retrieval_init_ms,
            2,
        ),
        "answer": answer,
        "error": error,
    }


def calculate_percentile(
    values,
    percentile,
):
    """
    Calculate an interpolated percentile.
    """
    if not values:
        return 0.0

    sorted_values = sorted(values)

    index = (
        len(sorted_values) - 1
    ) * percentile

    lower = int(index)

    upper = min(
        lower + 1,
        len(sorted_values) - 1,
    )

    weight = index - lower

    return (
        sorted_values[lower]
        + (
            sorted_values[upper]
            - sorted_values[lower]
        )
        * weight
    )


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

    completed = (
        passed + failed
    )

    completion_rate = (
        completed / total * 100
        if total
        else 0.0
    )

    pass_rate_completed = (
        passed / completed * 100
        if completed
        else 0.0
    )

    error_rate = (
        errors / total * 100
        if total
        else 0.0
    )

    print(
        "\n" + "=" * 60
    )

    print(
        "ROUTING EVALUATION SUMMARY"
    )

    print(
        "=" * 60
    )

    print(
        f"Total queries : {total}"
    )

    print(
        f"Passed        : {passed}"
    )

    print(
        f"Failed        : {failed}"
    )

    print(
        f"Errors        : {errors}"
    )

    print(
        f"Completed     : {completed}"
    )

    print(
        f"Completion    : "
        f"{completion_rate:.2f}%"
    )

    print(
        f"Pass rate     : "
        f"{pass_rate_completed:.2f}% "
        f"(excluding infrastructure errors)"
    )

    print(
        f"Error rate    : "
        f"{error_rate:.2f}%"
    )

    print(
        "\nCategory breakdown:"
    )

    categories = sorted(
        {
            result["category"]
            for result in results
        }
    )

    for category in categories:
        category_results = [
            result
            for result in results
            if result["category"]
            == category
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

        category_completed = (
            category_passed
            + category_failed
        )

        rate = (
            category_passed
            / category_completed
            * 100
            if category_completed
            else 0.0
        )

        print(
            f"  {category}: "
            f"{category_passed}/"
            f"{category_completed} "
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
        p50 = calculate_percentile(
            latencies,
            0.50,
        )

        p95 = calculate_percentile(
            latencies,
            0.95,
        )

        print("\nLatency:")

        print(
            f"  Average : "
            f"{statistics.mean(latencies):.2f} ms"
        )

        print(
            f"  P50     : "
            f"{p50:.2f} ms"
        )

        print(
            f"  P95     : "
            f"{p95:.2f} ms"
        )

    cold_results = [
        result
        for result in results
        if result.get(
            "retrieval_cold_start"
        )
        and result["error"] is None
    ]

    warm_results = [
        result
        for result in results
        if not result.get(
            "retrieval_cold_start"
        )
        and result["error"] is None
    ]

    print(
        "\nCold-start vs warm-request latency:"
    )

    if cold_results:
        cold_latencies = [
            result["latency_ms"]
            for result in cold_results
        ]

        init_times = [
            result["retrieval_init_ms"]
            for result in cold_results
        ]

        print(
            f"  Cold-start requests : "
            f"{len(cold_results)}"
        )

        print(
            f"  Cold-start average  : "
            f"{statistics.mean(cold_latencies):.2f} ms"
        )

        print(
            f"  Retrieval init      : "
            f"{statistics.mean(init_times):.2f} ms"
        )

        print(
            f"  Cold-start max      : "
            f"{max(cold_latencies):.2f} ms"
        )

    else:
        print(
            "  Cold-start requests : 0"
        )

    if warm_results:
        warm_latencies = [
            result["latency_ms"]
            for result in warm_results
        ]

        print(
            f"  Warm requests       : "
            f"{len(warm_results)}"
        )

        print(
            f"  Warm average        : "
            f"{statistics.mean(warm_latencies):.2f} ms"
        )

        print(
            f"  Warm P50            : "
            f"{statistics.median(warm_latencies):.2f} ms"
        )

        print(
            f"  Warm max            : "
            f"{max(warm_latencies):.2f} ms"
        )

    else:
        print(
            "  Warm requests       : 0"
        )

    print(
        "\nFailed cases:"
    )

    failures = [
        result
        for result in results
        if result["status"] == "FAIL"
    ]

    if not failures:
        print("  None")

    else:
        for result in failures:
            print(
                f"\n  {result['id']}:"
            )

            print(
                f"    Question: "
                f"{result['question']}"
            )

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

    print(
        "\nInfrastructure errors:"
    )

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

    print(
        f"Loaded {len(dataset)} "
        "evaluation cases."
    )

    print(
        f"Evaluation delay: "
        f"{EVALUATION_DELAY_SECONDS:.1f}s"
    )

    print(
        f"Rate-limit retries: "
        f"{MAX_RATE_LIMIT_RETRIES}"
    )

    results = []

    for index, case in enumerate(
        dataset
    ):
        # Add a delay between cases to avoid
        # sending a burst of requests into the
        # provider's per-minute token window.
        if (
            index > 0
            and EVALUATION_DELAY_SECONDS > 0
        ):
            print(
                f"\nWaiting "
                f"{EVALUATION_DELAY_SECONDS:.1f}s "
                "before next evaluation..."
            )

            time.sleep(
                EVALUATION_DELAY_SECONDS
            )

        result = evaluate_case(
            case
        )

        results.append(result)

        print(
            f"  {result['status']} | "
            f"tool={result['actual_tool']} | "
            f"latency="
            f"{result['latency_ms']:.2f} ms"
        )

    RESULTS_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

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

    completed = (
        passed + failed
    )

    completion_rate = (
        completed / total
        if total
        else 0.0
    )

    pass_rate_completed = (
        passed / completed
        if completed
        else 0.0
    )

    error_rate = (
        errors / total
        if total
        else 0.0
    )

    with open(
        RESULTS_PATH,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            {
                "total_cases": total,
                "summary": {
                    "total_cases": total,
                    "passed": passed,
                    "failed": failed,
                    "errors": errors,
                    "completed_cases": completed,
                    "completion_rate": round(
                        completion_rate,
                        4,
                    ),
                    "pass_rate_completed": round(
                        pass_rate_completed,
                        4,
                    ),
                    "error_rate": round(
                        error_rate,
                        4,
                    ),
                },
                "results": results,
            },
            f,
            indent=2,
            ensure_ascii=False,
        )

    print_summary(
        results
    )

    print(
        f"\nResults saved to: "
        f"{RESULTS_PATH}"
    )


if __name__ == "__main__":
    main()
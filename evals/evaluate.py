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


def safe_mean(values):
    """Return the mean of a list, or 0.0 when empty."""
    if not values:
        return 0.0
    return statistics.mean(values)


def percentile(values, percentile_value):
    """Calculate an interpolated percentile."""
    if not values:
        return 0.0

    values = sorted(values)

    index = (
        len(values) - 1
    ) * percentile_value

    lower = int(index)
    upper = min(lower + 1, len(values) - 1)

    weight = index - lower

    return (
        values[lower]
        + (values[upper] - values[lower]) * weight
    )


def load_dataset():
    with open(
        DATASET_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def normalize(value):
    """Normalize text for keyword matching."""
    return str(value).lower().strip()


def check_keywords(answer, expected_keywords):
    """Return True when all expected keywords are present."""
    answer_text = normalize(answer)

    return all(
        normalize(keyword) in answer_text
        for keyword in expected_keywords
    )


def check_sources(actual_sources, expected_sources):
    """
    Return True when every expected source is present.

    An empty expected source list is valid for out-of-scope
    cases when the agent correctly returns no sources.
    """
    actual = {
        normalize(source)
        for source in (actual_sources or [])
    }

    expected = {
        normalize(source)
        for source in (expected_sources or [])
    }

    return expected.issubset(actual)


def estimate_cost(
    prompt_tokens,
    completion_tokens,
    model="openai/gpt-oss-20b",
):
    """
    Estimate Groq GPT-OSS cost.

    Pricing used:
      GPT-OSS-20B:
        input  = $0.075 / 1M tokens
        output = $0.30 / 1M tokens

      GPT-OSS-120B:
        input  = $0.15 / 1M tokens
        output = $0.60 / 1M tokens
    """
    if "120b" in model.lower():
        input_cost = 0.15
        output_cost = 0.60
    else:
        input_cost = 0.075
        output_cost = 0.30

    return (
        (prompt_tokens / 1_000_000) * input_cost
        + (completion_tokens / 1_000_000) * output_cost
    )


def main():
    dataset = load_dataset()

    results = []

    latencies = []
    successful_latencies = []

    prompt_token_values = []
    completion_token_values = []
    reasoning_token_values = []
    total_token_values = []
    cost_values = []

    category_stats = defaultdict(
        lambda: {
            "total": 0,
            "passed": 0,
            "errors": 0,
        }
    )

    print("=" * 60)
    print("PRODUCTION EVALUATION")
    print("=" * 60)

    for case in dataset:
        case_id = case["id"]
        category = case["category"]
        question = case["question"]

        category_stats[category]["total"] += 1

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

            latency_ms = (
                time.perf_counter() - start
            ) * 1000

            latencies.append(latency_ms)
            successful_latencies.append(latency_ms)

            answer = result.get("answer", "")
            sources = result.get("sources", [])
            tools_used = result.get(
                "tools_used",
                [],
            )

            retrieval_metadata = result.get(
                "retrieval_metadata",
                {},
            )

            llm_metadata = result.get(
                "llm_metadata",
                {},
            ) or {}

            expected_keywords = case.get(
                "expected_keywords",
                [],
            )

            expected_sources = case.get(
                "expected_sources",
                [],
            )

            keyword_pass = check_keywords(
                answer,
                expected_keywords,
            )

            source_pass = check_sources(
                sources,
                expected_sources,
            )

            passed = (
                keyword_pass
                and source_pass
            )

            if passed:
                category_stats[category]["passed"] += 1

            # Token / cost metadata
            prompt_tokens = (
                llm_metadata.get(
                    "prompt_tokens",
                    0,
                )
                or 0
            )

            completion_tokens = (
                llm_metadata.get(
                    "completion_tokens",
                    0,
                )
                or 0
            )

            reasoning_tokens = (
                llm_metadata.get(
                    "reasoning_tokens",
                    0,
                )
                or 0
            )

            total_tokens = (
                llm_metadata.get(
                    "total_tokens",
                    0,
                )
                or 0
            )

            cost_usd = (
                llm_metadata.get(
                    "cost_usd",
                    0.0,
                )
                or 0.0
            )

            # If the LLM layer did not provide cost,
            # calculate it from token usage.
            if (
                cost_usd == 0.0
                and (
                    prompt_tokens
                    or completion_tokens
                )
            ):
                cost_usd = estimate_cost(
                    prompt_tokens,
                    completion_tokens,
                    llm_metadata.get(
                        "model",
                        "openai/gpt-oss-20b",
                    ),
                )

            if prompt_tokens:
                prompt_token_values.append(
                    prompt_tokens
                )

            if completion_tokens:
                completion_token_values.append(
                    completion_tokens
                )

            if reasoning_tokens:
                reasoning_token_values.append(
                    reasoning_tokens
                )

            if total_tokens:
                total_token_values.append(
                    total_tokens
                )

            if cost_usd:
                cost_values.append(
                    cost_usd
                )

            case_result = {
                "id": case_id,
                "category": category,
                "question": question,
                "passed": passed,
                "keyword_pass": keyword_pass,
                "source_pass": source_pass,
                "answer": answer,
                "sources": sources,
                "expected_sources": expected_sources,
                "tools_used": tools_used,
                "latency_ms": round(
                    latency_ms,
                    2,
                ),
                "retrieval_metadata": (
                    retrieval_metadata
                ),
                "llm_metadata": llm_metadata,
                "cost_usd": round(
                    cost_usd,
                    8,
                ),
            }

            results.append(case_result)

            print(
                f"Result: {'PASS' if passed else 'FAIL'}"
            )
            print(
                f"Latency: {latency_ms:.2f} ms"
            )
            print(
                f"Answer: {answer}"
            )
            print(
                f"Sources: {sources}"
            )
            print(
                f"Expected sources: "
                f"{expected_sources}"
            )
            print(
                f"Source hit: {source_pass}"
            )
            print(
                f"Tools used: {tools_used}"
            )
            print(
                f"Retrieval metadata: "
                f"{retrieval_metadata}"
            )

        except Exception as error:  # noqa: BLE001
            latency_ms = (
                time.perf_counter() - start
            ) * 1000

            latencies.append(latency_ms)

            category_stats[category]["errors"] += 1

            results.append(
                {
                    "id": case_id,
                    "category": category,
                    "question": question,
                    "passed": False,
                    "error": str(error),
                    "latency_ms": round(
                        latency_ms,
                        2,
                    ),
                }
            )

            print(
                f"Result: ERROR - {error}"
            )

    # ---------------------------------------------------------
    # SUMMARY
    # ---------------------------------------------------------

    total_cases = len(results)

    passed_cases = sum(
        1
        for result in results
        if result.get("passed") is True
    )

    failed_cases = sum(
        1
        for result in results
        if result.get("passed") is False
        and "error" not in result
    )

    error_cases = sum(
        1
        for result in results
        if "error" in result
    )

    completed_cases = (
        total_cases - error_cases
    )

    completion_rate = (
        completed_cases / total_cases
        if total_cases
        else 0.0
    )

    pass_rate = (
        passed_cases / completed_cases
        if completed_cases
        else 0.0
    )

    error_rate = (
        error_cases / total_cases
        if total_cases
        else 0.0
    )

    average_latency = safe_mean(
        latencies
    )

    p50_latency = percentile(
        latencies,
        0.50,
    )

    p95_latency = percentile(
        latencies,
        0.95,
    )

    # ---------------------------------------------------------
    # RETRIEVAL QUALITY
    # ---------------------------------------------------------

    in_scope_cases = [
        result
        for result in results
        if next(
            (
                item
                for item in dataset
                if item["id"] == result["id"]
            ),
            {},
        ).get(
            "category"
        ) != "Out-of-scope"
        and "error" not in result
    ]

    out_of_scope_cases = [
        result
        for result in results
        if next(
            (
                item
                for item in dataset
                if item["id"] == result["id"]
            ),
            {},
        ).get(
            "category"
        ) == "Out-of-scope"
        and "error" not in result
    ]

    in_scope_with_expected_source = [
        result
        for result in in_scope_cases
        if result.get("source_pass") is True
    ]

    in_scope_retrieval_success_rate = (
        len(in_scope_with_expected_source)
        / len(in_scope_cases)
        if in_scope_cases
        else 0.0
    )

    out_of_scope_no_evidence_cases = [
        result
        for result in out_of_scope_cases
        if not result.get("sources")
        and not result.get(
            "retrieval_metadata",
            {},
        ).get("documents_retrieved")
    ]

    out_of_scope_no_evidence_rate = (
        len(out_of_scope_no_evidence_cases)
        / len(out_of_scope_cases)
        if out_of_scope_cases
        else 0.0
    )

    source_hit_rate = (
        len(
            [
                result
                for result in results
                if result.get("source_pass")
            ]
        )
        / completed_cases
        if completed_cases
        else 0.0
    )

    document_counts = []

    retrieval_distances = []

    for result in results:
        metadata = result.get(
            "retrieval_metadata",
            {},
        )

        if metadata:
            document_count = metadata.get(
                "documents_retrieved"
            )

            if document_count is not None:
                document_counts.append(
                    document_count
                )

            scores = metadata.get(
                "scores",
                [],
            )

            retrieval_distances.extend(
                float(score)
                for score in scores
            )

    average_documents_retrieved = safe_mean(
        document_counts
    )

    average_retrieval_distance = safe_mean(
        retrieval_distances
    )

    # ---------------------------------------------------------
    # COLD / WARM LATENCY
    # ---------------------------------------------------------

    cold_start_latency = (
        successful_latencies[0]
        if successful_latencies
        else 0.0
    )

    warm_latencies = (
        successful_latencies[1:]
        if len(successful_latencies) > 1
        else []
    )

    warm_average_latency = safe_mean(
        warm_latencies
    )

    warm_p50_latency = percentile(
        warm_latencies,
        0.50,
    )

    warm_p95_latency = percentile(
        warm_latencies,
        0.95,
    )

    # ---------------------------------------------------------
    # COST / TOKEN METRICS
    # ---------------------------------------------------------

    average_prompt_tokens = safe_mean(
        prompt_token_values
    )

    average_completion_tokens = safe_mean(
        completion_token_values
    )

    average_reasoning_tokens = safe_mean(
        reasoning_token_values
    )

    average_total_tokens = safe_mean(
        total_token_values
    )

    average_cost_per_query = safe_mean(
        cost_values
    )

    total_cost = sum(
        cost_values
    )

    projected_cost_1k = (
        average_cost_per_query * 1_000
    )

    projected_cost_10k = (
        average_cost_per_query * 10_000
    )

    projected_cost_100k = (
        average_cost_per_query * 100_000
    )

    # ---------------------------------------------------------
    # PRINT REPORT
    # ---------------------------------------------------------

    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)

    print(
        f"Total cases: {total_cases}"
    )

    print(
        f"Passed: {passed_cases}"
    )

    print(
        f"Failed: {failed_cases}"
    )

    print(
        f"Errors: {error_cases}"
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
    print("RETRIEVAL QUALITY")
    print("-" * 60)

    print(
        f"Source hit rate: "
        f"{source_hit_rate * 100:.1f}%"
    )

    print(
        f"In-scope retrieval success: "
        f"{in_scope_retrieval_success_rate * 100:.1f}%"
    )

    print(
        f"In-scope cases with evidence: "
        f"{len(in_scope_with_expected_source)}"
        f"/{len(in_scope_cases)}"
    )

    print(
        f"Out-of-scope no-evidence: "
        f"{len(out_of_scope_no_evidence_cases)}"
        f"/{len(out_of_scope_cases)} "
        f"({out_of_scope_no_evidence_rate * 100:.1f}%)"
    )

    print(
        f"Average documents retrieved: "
        f"{average_documents_retrieved:.2f}"
    )

    print(
        f"Average retrieval distance: "
        f"{average_retrieval_distance:.4f}"
    )

    print()
    print("LATENCY DIAGNOSTICS")
    print("-" * 60)

    print(
        f"Cold-start latency: "
        f"{cold_start_latency:.2f} ms"
    )

    print(
        f"Warm average latency: "
        f"{warm_average_latency:.2f} ms"
    )

    print(
        f"Warm P50 latency: "
        f"{warm_p50_latency:.2f} ms"
    )

    print(
        f"Warm P95 latency: "
        f"{warm_p95_latency:.2f} ms"
    )

    print()
    print("COST / TOKEN METRICS")
    print("-" * 60)

    print(
        f"Average prompt tokens: "
        f"{average_prompt_tokens:.1f}"
    )

    print(
        f"Average completion tokens: "
        f"{average_completion_tokens:.1f}"
    )

    print(
        f"Average reasoning tokens: "
        f"{average_reasoning_tokens:.1f}"
    )

    print(
        f"Average total tokens: "
        f"{average_total_tokens:.1f}"
    )

    print(
        f"Average cost/query: "
        f"${average_cost_per_query:.8f}"
    )

    print(
        f"Total evaluation cost: "
        f"${total_cost:.8f}"
    )

    print(
        f"Projected cost at 1K queries: "
        f"${projected_cost_1k:.4f}"
    )

    print(
        f"Projected cost at 10K queries: "
        f"${projected_cost_10k:.4f}"
    )

    print(
        f"Projected cost at 100K queries: "
        f"${projected_cost_100k:.4f}"
    )

    print()
    print("BY CATEGORY")

    for category, stats in sorted(
        category_stats.items()
    ):
        completed = (
            stats["total"]
            - stats["errors"]
        )

        category_pass_rate = (
            stats["passed"] / completed
            if completed
            else 0.0
        )

        print(
            f"  {category}: "
            f"{stats['passed']}/"
            f"{completed} passed "
            f"({category_pass_rate * 100:.1f}%), "
            f"{stats['errors']} error(s)"
        )

    # ---------------------------------------------------------
    # JSON REPORT
    # ---------------------------------------------------------

    report = {
        "summary": {
            "total_cases": total_cases,
            "passed": passed_cases,
            "failed": failed_cases,
            "errors": error_cases,
            "completion_rate": round(
                completion_rate,
                4,
            ),
            "pass_rate": round(
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
            "cold_start_latency_ms": round(
                cold_start_latency,
                2,
            ),
            "warm_average_latency_ms": round(
                warm_average_latency,
                2,
            ),
            "warm_p50_latency_ms": round(
                warm_p50_latency,
                2,
            ),
            "warm_p95_latency_ms": round(
                warm_p95_latency,
                2,
            ),
        },
        "retrieval": {
            "source_hit_rate": round(
                source_hit_rate,
                4,
            ),
            "in_scope_retrieval_success_rate": round(
                in_scope_retrieval_success_rate,
                4,
            ),
            "in_scope_cases_with_evidence": (
                len(in_scope_with_expected_source)
            ),
            "in_scope_case_count": (
                len(in_scope_cases)
            ),
            "out_of_scope_no_evidence_rate": round(
                out_of_scope_no_evidence_rate,
                4,
            ),
            "out_of_scope_no_evidence_cases": (
                len(out_of_scope_no_evidence_cases)
            ),
            "out_of_scope_case_count": (
                len(out_of_scope_cases)
            ),
            "average_documents_retrieved": round(
                average_documents_retrieved,
                2,
            ),
            "average_retrieval_distance": round(
                average_retrieval_distance,
                4,
            ),
        },
        "cost": {
            "average_prompt_tokens": round(
                average_prompt_tokens,
                2,
            ),
            "average_completion_tokens": round(
                average_completion_tokens,
                2,
            ),
            "average_reasoning_tokens": round(
                average_reasoning_tokens,
                2,
            ),
            "average_total_tokens": round(
                average_total_tokens,
                2,
            ),
            "average_cost_per_query_usd": round(
                average_cost_per_query,
                8,
            ),
            "total_evaluation_cost_usd": round(
                total_cost,
                8,
            ),
            "projected_cost_1k_usd": round(
                projected_cost_1k,
                4,
            ),
            "projected_cost_10k_usd": round(
                projected_cost_10k,
                4,
            ),
            "projected_cost_100k_usd": round(
                projected_cost_100k,
                4,
            ),
        },
        "category_stats": dict(
            category_stats
        ),
        "results": results,
        "limitations": [
            "The evaluation dataset currently contains only five cases.",
            "Keyword matching is not equivalent to semantic answer evaluation.",
            "Cold-start latency is based on the first successful evaluation case and is not a controlled process-restart benchmark.",
            "Cost projections assume the evaluation average represents production traffic.",
            "Retrieval distance is embedding-model-specific and should not be interpreted as a universal relevance threshold.",
        ],
    }

    with open(
        RESULTS_PATH,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            report,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print()
    print(
        f"Evaluation results saved to: "
        f"{RESULTS_PATH}"
    )


if __name__ == "__main__":
    main()
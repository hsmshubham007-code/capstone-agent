import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EVALS_DIR = PROJECT_ROOT / "evals"

PASS_RATE_THRESHOLD = 0.90
RETRIEVAL_GATE_K = 2

EVALUATIONS = [
    {
        "name": "Routing",
        "module": "evals.evaluate_routing",
        "result_file": EVALS_DIR / "routing_evaluation_results.json",
    },
    {
        "name": "Retrieval",
        "module": "evals.evaluate_retrieval",
        "result_file": EVALS_DIR / "retrieval_evaluation_results.json",
    },
    {
        "name": "Prompt Injection",
        "module": "evals.evaluate_injection",
        "result_file": EVALS_DIR / "injection_results.json",
    },
]


def run_evaluation(name, module):
    print()
    print("=" * 70)
    print(f"RUNNING {name.upper()} EVALUATION")
    print("=" * 70)

    process = subprocess.run(
    [sys.executable, "-m", module],
    cwd=PROJECT_ROOT,
    check=False,
   )

    return process.returncode


def load_json(path):
    if not path.exists():
        return None

    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except (OSError, json.JSONDecodeError):
        return None


def normalize_rate(value):
    """
    Accept both decimal rates such as 0.95 and
    percentage values such as 95.
    """

    if value > 1:
        return value / 100

    return value


def extract_standard_pass_rate(data):
    """
    Extract a pass rate from the standard evaluation
    result formats used by routing and injection tests.
    """

    if not isinstance(data, dict):
        return None

    results = data.get("results")

    if isinstance(results, list) and results:
        total = len(results)

        passed = sum(
            1
            for result in results
            if (
                result.get("passed") is True
                or result.get("status") == "PASS"
            )
        )

        return passed / total

    summary = data.get("summary")

    if isinstance(summary, dict):
        pass_rate = summary.get("pass_rate")

        if isinstance(pass_rate, (int, float)):
            return normalize_rate(pass_rate)

        passed = summary.get("passed")
        total = summary.get("total")

        if (
            isinstance(passed, (int, float))
            and isinstance(total, (int, float))
            and total > 0
        ):
            return passed / total

    pass_rate = data.get("pass_rate")

    if isinstance(pass_rate, (int, float)):
        return normalize_rate(pass_rate)

    passed = data.get("passed")
    total = data.get("total")

    if (
        isinstance(passed, (int, float))
        and isinstance(total, (int, float))
        and total > 0
    ):
        return passed / total

    return None


def extract_retrieval_metrics(data):
    """
    Extract the retrieval metrics for the configured
    production gate K value.
    """

    if not isinstance(data, dict):
        return None

    results = data.get("results")

    if not isinstance(results, dict):
        return None

    k_key = str(RETRIEVAL_GATE_K)
    k_result = results.get(k_key)

    if not isinstance(k_result, dict):
        return None

    in_scope_rate = k_result.get(
        "in_scope_success_rate"
    )

    out_of_scope_rate = k_result.get(
        "out_of_scope_no_evidence_rate"
    )

    if not isinstance(in_scope_rate, (int, float)):
        return None

    if not isinstance(out_of_scope_rate, (int, float)):
        return None

    return {
        "k": RETRIEVAL_GATE_K,
        "in_scope_success_rate": normalize_rate(
            in_scope_rate
        ),
        "out_of_scope_no_evidence_rate": normalize_rate(
            out_of_scope_rate
        ),
        "in_scope_success": k_result.get(
            "in_scope_success",
            0,
        ),
        "in_scope_total": k_result.get(
            "in_scope_total",
            0,
        ),
        "out_of_scope_no_evidence": k_result.get(
            "out_of_scope_no_evidence",
            0,
        ),
        "out_of_scope_total": k_result.get(
            "out_of_scope_total",
            0,
        ),
    }


def print_standard_result(
    name,
    return_code,
    result_file,
):
    data = load_json(result_file)

    pass_rate = extract_standard_pass_rate(data)

    print()
    print(f"{name}:")
    print(f"  Process exit code : {return_code}")

    if pass_rate is None:
        print("  Pass rate         : unavailable")
        print("  Gate status       : UNKNOWN")

        return {
            "name": name,
            "return_code": return_code,
            "pass_rate": None,
            "status": "UNKNOWN",
        }

    print(
        f"  Pass rate         : "
        f"{pass_rate * 100:.2f}%"
    )

    print(
        f"  Required          : "
        f"{PASS_RATE_THRESHOLD * 100:.2f}%"
    )

    if (
        return_code != 0
        or pass_rate < PASS_RATE_THRESHOLD
    ):
        status = "FAIL"
    else:
        status = "PASS"

    print(f"  Gate status       : {status}")

    return {
        "name": name,
        "return_code": return_code,
        "pass_rate": round(pass_rate, 4),
        "status": status,
    }


def print_retrieval_result(
    return_code,
    result_file,
):
    data = load_json(result_file)

    metrics = extract_retrieval_metrics(data)

    print()
    print("Retrieval:")
    print(f"  Process exit code : {return_code}")

    if metrics is None:
        print("  Top-2 pass rate   : unavailable")
        print("  Gate status       : UNKNOWN")

        return {
            "name": "Retrieval",
            "return_code": return_code,
            "pass_rate": None,
            "status": "UNKNOWN",
        }

    in_scope_rate = metrics[
        "in_scope_success_rate"
    ]

    out_of_scope_rate = metrics[
        "out_of_scope_no_evidence_rate"
    ]

    print(
        f"  Top-{metrics['k']} in-scope    : "
        f"{metrics['in_scope_success']}/"
        f"{metrics['in_scope_total']} "
        f"({in_scope_rate * 100:.2f}%)"
    )

    print(
        f"  Out-of-scope clean : "
        f"{metrics['out_of_scope_no_evidence']}/"
        f"{metrics['out_of_scope_total']} "
        f"({out_of_scope_rate * 100:.2f}%)"
    )

    print(
        f"  Required           : "
        f"{PASS_RATE_THRESHOLD * 100:.2f}%"
    )

    if (
        return_code != 0
        or in_scope_rate < PASS_RATE_THRESHOLD
        or out_of_scope_rate < PASS_RATE_THRESHOLD
    ):
        status = "FAIL"
    else:
        status = "PASS"

    print(f"  Gate status        : {status}")

    return {
        "name": "Retrieval",
        "return_code": return_code,
        "pass_rate": round(in_scope_rate, 4),
        "out_of_scope_clean_rate": round(
            out_of_scope_rate,
            4,
        ),
        "gate_k": RETRIEVAL_GATE_K,
        "status": status,
    }


def main():
    print("=" * 70)
    print("COMPANY POLICY AGENT - EVALUATION SUITE")
    print("=" * 70)

    print()
    print(
        f"Required pass-rate threshold: "
        f"{PASS_RATE_THRESHOLD * 100:.0f}%"
    )

    print(
        f"Retrieval gate K: "
        f"Top-{RETRIEVAL_GATE_K}"
    )

    results = []

    for evaluation in EVALUATIONS:
        return_code = run_evaluation(
            evaluation["name"],
            evaluation["module"],
        )

        if evaluation["name"] == "Retrieval":
            result = print_retrieval_result(
                return_code,
                evaluation["result_file"],
            )
        else:
            result = print_standard_result(
                evaluation["name"],
                return_code,
                evaluation["result_file"],
            )

        results.append(result)

    # ---------------------------------------------------------
    # OVERALL GATE
    # ---------------------------------------------------------

    failed = [
        result
        for result in results
        if result["status"] != "PASS"
    ]

    print()
    print("=" * 70)
    print("EVALUATION SUITE SUMMARY")
    print("=" * 70)

    for result in results:
        pass_rate = result.get("pass_rate")

        if pass_rate is None:
            rate_text = "unavailable"
        else:
            rate_text = (
                f"{pass_rate * 100:.2f}%"
            )

        print(
            f"{result['name']:<20} "
            f"{rate_text:<15} "
            f"{result['status']}"
        )

    print()

    if failed:
        print("EVALUATION GATE: FAIL")
        print()
        print("Failed evaluations:")

        for result in failed:
            print(
                f"  - {result['name']}: "
                f"{result['status']}"
            )

        print()
        print(
            "The evaluation suite returned "
            "a non-zero exit code."
        )

        return 1

    print("EVALUATION GATE: PASS")
    print()
    print(
        "All evaluation suites passed the "
        f"{PASS_RATE_THRESHOLD * 100:.0f}% threshold."
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
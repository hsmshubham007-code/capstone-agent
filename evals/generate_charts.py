import json
from pathlib import Path

import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EVALS_DIR = PROJECT_ROOT / "evals"
CHARTS_DIR = EVALS_DIR / "charts"

CHARTS_DIR.mkdir(exist_ok=True)


def load_json(filename):
    with open(EVALS_DIR / filename, "r", encoding="utf-8") as file:
        return json.load(file)


def create_cost_chart():
    data = load_json("cost_projection.json")

    base = data["monthly_base"]
    projected = data["monthly_10x"]

    labels = [
        "Always 20B",
        "Routed",
        "Always 120B",
    ]

    base_values = [
        base["always_20b_usd"],
        base["routed_usd"],
        base["always_120b_usd"],
    ]

    projected_values = [
        projected["always_20b_usd"],
        projected["routed_usd"],
        projected["always_120b_usd"],
    ]

    x = range(len(labels))
    width = 0.35

    fig, ax = plt.subplots(figsize=(9, 6))

    x_base = [i - width / 2 for i in x]
    x_projected = [i + width / 2 for i in x]

    ax.bar(
        x_base,
        base_values,
        width,
        label="10K queries/month",
    )

    ax.bar(
        x_projected,
        projected_values,
        width,
        label="100K queries/month",
    )

    ax.set_title("Monthly LLM Cost Projection")
    ax.set_ylabel("Estimated USD")
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels)
    ax.legend()

    for positions, values in [
        (x_base, base_values),
        (x_projected, projected_values),
    ]:
        for position, value in zip(positions, values):
            ax.text(
                position,
                value,
                f"${value:.2f}",
                ha="center",
                va="bottom",
            )

    fig.tight_layout()
    fig.savefig(
        CHARTS_DIR / "monthly_cost_projection.png",
        dpi=150,
    )
    plt.close(fig)


def create_latency_chart():
    data = load_json("evaluation_results.json")

    summary = data["summary"]

    labels = [
        "Average",
        "P50",
        "P95",
    ]

    values = [
        summary["average_latency_ms"],
        summary["p50_latency_ms"],
        summary["p95_latency_ms"],
    ]

    fig, ax = plt.subplots(figsize=(8, 6))

    bars = ax.bar(labels, values)

    ax.set_title("Evaluation Latency")
    ax.set_ylabel("Latency (ms)")

    for bar, value in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{value:,.0f} ms",
            ha="center",
            va="bottom",
        )

    fig.tight_layout()
    fig.savefig(
        CHARTS_DIR / "latency_metrics.png",
        dpi=150,
    )
    plt.close(fig)


def create_category_chart():
    data = load_json("evaluation_results.json")

    # Current evaluation schema stores category data here.
    categories = data["category_stats"]

    labels = list(categories.keys())

    pass_rates = []

    for name in labels:
        total = categories[name]["total"]
        passed = categories[name]["passed"]

        if total == 0:
            pass_rate = 0
        else:
            pass_rate = (passed / total) * 100

        pass_rates.append(pass_rate)

    fig, ax = plt.subplots(figsize=(9, 6))

    bars = ax.bar(labels, pass_rates)

    ax.set_title("Evaluation Pass Rate by Query Category")
    ax.set_ylabel("Pass Rate (%)")
    ax.set_ylim(0, 100)

    for bar, value in zip(bars, pass_rates):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{value:.0f}%",
            ha="center",
            va="bottom",
        )

    fig.tight_layout()
    fig.savefig(
        CHARTS_DIR / "category_pass_rate.png",
        dpi=150,
    )
    plt.close(fig)


def create_retrieval_chart():
    data = load_json("evaluation_results.json")

    retrieval = data["retrieval"]

    labels = [
        "Source Hit Rate",
        "In-Scope Retrieval",
        "Out-of-Scope\nNo Evidence",
    ]

    values = [
        retrieval["source_hit_rate"] * 100,
        retrieval["in_scope_retrieval_success_rate"] * 100,
        retrieval["out_of_scope_no_evidence_rate"] * 100,
    ]

    fig, ax = plt.subplots(figsize=(9, 6))

    bars = ax.bar(labels, values)

    ax.set_title("Retrieval Quality")
    ax.set_ylabel("Rate (%)")
    ax.set_ylim(0, 100)

    for bar, value in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{value:.0f}%",
            ha="center",
            va="bottom",
        )

    fig.tight_layout()
    fig.savefig(
        CHARTS_DIR / "retrieval_quality.png",
        dpi=150,
    )
    plt.close(fig)


def create_warm_latency_chart():
    data = load_json("evaluation_results.json")

    summary = data["summary"]

    labels = [
        "Cold Start",
        "Warm Average",
        "Warm P50",
        "Warm P95",
    ]

    values = [
        summary["cold_start_latency_ms"],
        summary["warm_average_latency_ms"],
        summary["warm_p50_latency_ms"],
        summary["warm_p95_latency_ms"],
    ]

    fig, ax = plt.subplots(figsize=(9, 6))

    bars = ax.bar(labels, values)

    ax.set_title("Cold-Start vs Warm Latency")
    ax.set_ylabel("Latency (ms)")

    for bar, value in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{value:,.0f} ms",
            ha="center",
            va="bottom",
        )

    fig.tight_layout()
    fig.savefig(
        CHARTS_DIR / "cold_vs_warm_latency.png",
        dpi=150,
    )
    plt.close(fig)


def create_injection_chart():
    data = load_json("injection_results.json")

    summary = data["summary"]

    passed = summary["passed_cases"]
    failed = summary["failed_cases"]
    errors = summary.get("error_cases", 0)

    labels = [
        "Passed",
        "Failed",
        "Errors",
    ]

    values = [
        passed,
        failed,
        errors,
    ]

    fig, ax = plt.subplots(figsize=(8, 6))

    bars = ax.bar(labels, values)

    ax.set_title("Prompt Injection Evaluation")
    ax.set_ylabel("Number of Cases")

    for bar, value in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            str(value),
            ha="center",
            va="bottom",
        )

    fig.tight_layout()
    fig.savefig(
        CHARTS_DIR / "injection_evaluation.png",
        dpi=150,
    )
    plt.close(fig)


def main():
    create_cost_chart()
    create_latency_chart()
    create_category_chart()
    create_retrieval_chart()
    create_warm_latency_chart()
    create_injection_chart()

    print("=" * 60)
    print("EVALUATION CHARTS GENERATED")
    print("=" * 60)

    for chart in sorted(CHARTS_DIR.glob("*.png")):
        print(chart)


if __name__ == "__main__":
    main()
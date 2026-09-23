import json
import statistics
from collections import defaultdict

RESULTS_FILE = "evals/routing_evaluation_results.json"


def percentile(values, percentile):
    values = sorted(values)

    if not values:
        return 0

    if len(values) == 1:
        return values[0]

    index = (len(values) - 1) * percentile / 100
    lower = int(index)
    upper = min(lower + 1, len(values) - 1)

    if lower == upper:
        return values[lower]

    weight = index - lower
    return values[lower] + (values[upper] - values[lower]) * weight


with open(RESULTS_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)


results = data["results"]

by_category = defaultdict(list)

for result in results:
    latency = result.get("latency_ms")

    if latency is not None:
        by_category[result["category"]].append(latency)


print("=" * 70)
print("LATENCY ANALYSIS")
print("=" * 70)

print()

for category, latencies in sorted(by_category.items()):
    print(f"{category}")
    print("-" * 70)

    print(f"Queries : {len(latencies)}")
    print(f"Average : {statistics.mean(latencies):.2f} ms")
    print(f"P50     : {percentile(latencies, 50):.2f} ms")
    print(f"P95     : {percentile(latencies, 95):.2f} ms")
    print(f"Min     : {min(latencies):.2f} ms")
    print(f"Max     : {max(latencies):.2f} ms")

    print()


print("=" * 70)
print("SLOWEST QUERIES")
print("=" * 70)

slowest = sorted(
    results,
    key=lambda x: x.get("latency_ms", 0),
    reverse=True,
)

for result in slowest[:10]:
    print(
        f"{result['id']:15} "
        f"{result['category']:15} "
        f"{result.get('latency_ms', 0):10.2f} ms | "
        f"{result['question']}"
    )
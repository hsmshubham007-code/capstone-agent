import threading
from collections import defaultdict


class Metrics:
    def __init__(self):
        self._lock = threading.Lock()

        self.counters = defaultdict(int)

        self.latencies = []

        self.llm_usage = {
            "requests": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
        }

        self.cost = {
            "total_usd": 0.0,
            "requests_with_cost": 0,
        }

    def increment(self, name, value=1):
        with self._lock:
            self.counters[name] += value

    def observe_latency(self, value):
        with self._lock:
            self.latencies.append(value)

            if len(self.latencies) > 1000:
                self.latencies = self.latencies[-1000:]

    def record_llm_usage(
        self,
        prompt_tokens=0,
        completion_tokens=0,
        total_tokens=0,
    ):
        with self._lock:
            self.llm_usage["requests"] += 1
            self.llm_usage["prompt_tokens"] += prompt_tokens
            self.llm_usage["completion_tokens"] += completion_tokens
            self.llm_usage["total_tokens"] += total_tokens

    def record_cost(self, cost_usd):
        with self._lock:
            self.cost["total_usd"] += cost_usd
            self.cost["requests_with_cost"] += 1

    def _percentile(self, values, percentile):
        if not values:
            return 0

        sorted_values = sorted(values)
        index = (len(sorted_values) - 1) * percentile

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

    def snapshot(self):
        with self._lock:
            latency_values = list(self.latencies)

            average_latency = (
                sum(latency_values) / len(latency_values)
                if latency_values
                else 0
            )

            p50_latency = self._percentile(
                latency_values,
                0.50,
            )

            p95_latency = self._percentile(
                latency_values,
                0.95,
            )

            total_requests = self.counters.get(
                "requests_total",
                0,
            )

            total_errors = self.counters.get(
                "requests_errors_total",
                0,
            )

            error_rate = (
                total_errors / total_requests
                if total_requests
                else 0
            )

            cost_per_request = (
                self.cost["total_usd"]
                / self.cost["requests_with_cost"]
                if self.cost["requests_with_cost"]
                else 0
            )

            return {
                "counters": dict(self.counters),
                "latency": {
                    "count": len(latency_values),
                    "average_ms": round(
                        average_latency,
                        2,
                    ),
                    "p50_ms": round(
                        p50_latency,
                        2,
                    ),
                    "p95_ms": round(
                        p95_latency,
                        2,
                    ),
                    "last_ms": round(
                        latency_values[-1],
                        2,
                    )
                    if latency_values
                    else 0,
                },
                "error_rate": round(
                    error_rate,
                    4,
                ),
                "llm": dict(self.llm_usage),
                "cost": {
                    "total_usd": round(
                        self.cost["total_usd"],
                        6,
                    ),
                    "requests_with_cost": self.cost[
                        "requests_with_cost"
                    ],
                    "cost_per_request_usd": round(
                        cost_per_request,
                        6,
                    ),
                },
            }


metrics = Metrics()
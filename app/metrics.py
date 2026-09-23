import threading
from collections import defaultdict


class Metrics:
    def __init__(self):
        self._lock = threading.Lock()

        self.counters = defaultdict(int)

        # General HTTP latency.
        self.latencies = []

        # Chat-specific latency.
        self.chat_latencies = []

        # Retrieval-specific latency.
        self.retrieval_latencies = []

        # LLM-specific latency.
        self.llm_latencies = []

        # LLM token usage.
        self.llm_usage = {
            "requests": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
        }

        # Cost tracking.
        self.cost = {
            "total_usd": 0.0,
            "requests_with_cost": 0,
        }

    # =========================================================
    # Counters
    # =========================================================

    def increment(self, name, value=1):
        with self._lock:
            self.counters[name] += value

    # =========================================================
    # Latency metrics
    # =========================================================

    def observe_latency(self, value):
        with self._lock:
            self.latencies.append(value)
            self._trim(self.latencies)

    def observe_chat_latency(self, value):
        with self._lock:
            self.chat_latencies.append(value)
            self._trim(self.chat_latencies)

    def observe_retrieval_latency(self, value):
        with self._lock:
            self.retrieval_latencies.append(value)
            self._trim(self.retrieval_latencies)

    def observe_llm_latency(self, value):
        with self._lock:
            self.llm_latencies.append(value)
            self._trim(self.llm_latencies)

    @staticmethod
    def _trim(values, maximum=1000):
        if len(values) > maximum:
            del values[:-maximum]

    # =========================================================
    # LLM usage
    # =========================================================

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

    # =========================================================
    # Cost
    # =========================================================

    def record_cost(self, cost_usd):
        with self._lock:
            self.cost["total_usd"] += cost_usd
            self.cost["requests_with_cost"] += 1

    # =========================================================
    # Percentiles
    # =========================================================

    @staticmethod
    def _percentile(values, percentile):
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

    # =========================================================
    # Latency summary
    # =========================================================

    def _latency_summary(self, values):
        if not values:
            return {
                "count": 0,
                "average_ms": 0,
                "p50_ms": 0,
                "p95_ms": 0,
                "last_ms": 0,
            }

        average = sum(values) / len(values)

        return {
            "count": len(values),
            "average_ms": round(
                average,
                2,
            ),
            "p50_ms": round(
                self._percentile(
                    values,
                    0.50,
                ),
                2,
            ),
            "p95_ms": round(
                self._percentile(
                    values,
                    0.95,
                ),
                2,
            ),
            "last_ms": round(
                values[-1],
                2,
            ),
        }

    # =========================================================
    # Snapshot
    # =========================================================

    def snapshot(self):
        with self._lock:
            latency_values = list(
                self.latencies
            )

            chat_latency_values = list(
                self.chat_latencies
            )

            retrieval_latency_values = list(
                self.retrieval_latencies
            )

            llm_latency_values = list(
                self.llm_latencies
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
                "counters": dict(
                    self.counters
                ),

                "latency": self._latency_summary(
                    latency_values
                ),

                "chat_latency": self._latency_summary(
                    chat_latency_values
                ),

                "retrieval_latency": self._latency_summary(
                    retrieval_latency_values
                ),

                "llm_latency": self._latency_summary(
                    llm_latency_values
                ),

                "error_rate": round(
                    error_rate,
                    4,
                ),

                "llm": dict(
                    self.llm_usage
                ),

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
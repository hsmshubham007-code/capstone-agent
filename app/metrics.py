import threading
import time
from collections import defaultdict


class Metrics:
    """
    Simple thread-safe application metrics collector.

    This provides operational metrics without requiring
    an external monitoring service.
    """

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

    def increment(self, name, value=1):
        with self._lock:
            self.counters[name] += value

    def observe_latency(self, value):
        with self._lock:
            self.latencies.append(value)

            # Prevent unlimited memory growth.
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

            self.llm_usage[
                "prompt_tokens"
            ] += prompt_tokens

            self.llm_usage[
                "completion_tokens"
            ] += completion_tokens

            self.llm_usage[
                "total_tokens"
            ] += total_tokens

    def snapshot(self):
        with self._lock:

            latency_values = list(
                self.latencies
            )

            average_latency = (
                sum(latency_values)
                / len(latency_values)
                if latency_values
                else 0
            )

            return {
                "counters": dict(
                    self.counters
                ),
                "latency": {
                    "count": len(
                        latency_values
                    ),
                    "average_ms": round(
                        average_latency,
                        2,
                    ),
                    "last_ms": round(
                        latency_values[-1],
                        2,
                    )
                    if latency_values
                    else 0,
                },
                "llm": dict(
                    self.llm_usage
                ),
            }


metrics = Metrics()


def timed_operation():
    """
    Convenience timer for measuring an operation.
    """

    return time.perf_counter()
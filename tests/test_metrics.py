from app.metrics import Metrics


def test_metrics_counter():

    metrics = Metrics()

    metrics.increment(
        "requests"
    )

    metrics.increment(
        "requests"
    )

    snapshot = metrics.snapshot()

    assert (
        snapshot["counters"]["requests"]
        == 2
    )


def test_metrics_latency():

    metrics = Metrics()

    metrics.observe_latency(
        100
    )

    metrics.observe_latency(
        200
    )

    snapshot = metrics.snapshot()

    assert (
        snapshot["latency"]["count"]
        == 2
    )

    assert (
        snapshot["latency"]["average_ms"]
        == 150
    )


def test_llm_usage():

    metrics = Metrics()

    metrics.record_llm_usage(
        prompt_tokens=100,
        completion_tokens=50,
        total_tokens=150,
    )

    snapshot = metrics.snapshot()

    assert (
        snapshot["llm"]["requests"]
        == 1
    )

    assert (
        snapshot["llm"]["prompt_tokens"]
        == 100
    )

    assert (
        snapshot["llm"]["completion_tokens"]
        == 50
    )

    assert (
        snapshot["llm"]["total_tokens"]
        == 150
    )
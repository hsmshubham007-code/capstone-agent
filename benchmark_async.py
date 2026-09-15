import asyncio
import statistics
import time

from app.async_tools import run_tools_parallel, run_tools_sequential

# ============================================================
# TEST QUERIES
# ============================================================

QUERIES = [
    "What are the rules for professional conduct?",
    "What are the acceptable use rules for company IT systems?",
    "What are the company policies for employees?",
    "What are the rules regarding workplace behavior?",
    "What are the company's information security requirements?",
]


# ============================================================
# RUN SEQUENTIAL
# ============================================================

async def benchmark_sequential(query):

    start = time.perf_counter()

    await run_tools_sequential(query)

    latency = time.perf_counter() - start

    return latency


# ============================================================
# RUN PARALLEL
# ============================================================

async def benchmark_parallel(query):

    start = time.perf_counter()

    await run_tools_parallel(query)

    latency = time.perf_counter() - start

    return latency


# ============================================================
# MAIN BENCHMARK
# ============================================================

async def main():

    sequential_times = []
    parallel_times = []

    print("=" * 70)
    print("ASYNC CAPSTONE LATENCY BENCHMARK")
    print("=" * 70)

    for i, query in enumerate(QUERIES, 1):

        print(f"\nTest {i}/{len(QUERIES)}")
        print(f"Query: {query}")

        # -----------------------------------------
        # Sequential
        # -----------------------------------------

        sequential_latency = await benchmark_sequential(
            query
        )

        # -----------------------------------------
        # Parallel
        # -----------------------------------------

        parallel_latency = await benchmark_parallel(
            query
        )

        sequential_times.append(
            sequential_latency
        )

        parallel_times.append(
            parallel_latency
        )

        reduction = (
            sequential_latency
            - parallel_latency
        )

        reduction_percent = (
            reduction / sequential_latency
        ) * 100

        print(
            f"Sequential : "
            f"{sequential_latency:.3f} seconds"
        )

        print(
            f"Parallel   : "
            f"{parallel_latency:.3f} seconds"
        )

        print(
            f"Reduction  : "
            f"{reduction:.3f} seconds "
            f"({reduction_percent:.2f}%)"
        )

    # ========================================================
    # AVERAGES
    # ========================================================

    sequential_average = statistics.mean(
        sequential_times
    )

    parallel_average = statistics.mean(
        parallel_times
    )

    # ========================================================
    # MEDIANS
    # ========================================================

    sequential_median = statistics.median(
        sequential_times
    )

    parallel_median = statistics.median(
        parallel_times
    )

    # ========================================================
    # OVERALL REDUCTION
    # ========================================================

    reduction_seconds = (
        sequential_average
        - parallel_average
    )

    reduction_percent = (
        reduction_seconds
        / sequential_average
    ) * 100

    # ========================================================
    # RESULTS
    # ========================================================

    print("\n")
    print("=" * 70)
    print("FINAL RESULTS")
    print("=" * 70)

    print(
        f"\nAverage sequential latency : "
        f"{sequential_average:.3f} seconds"
    )

    print(
        f"Average parallel latency   : "
        f"{parallel_average:.3f} seconds"
    )

    print(
        f"\nAverage latency reduction  : "
        f"{reduction_seconds:.3f} seconds"
    )

    print(
        f"Latency reduction          : "
        f"{reduction_percent:.2f}%"
    )

    print(
        f"\nMedian sequential latency  : "
        f"{sequential_median:.3f} seconds"
    )

    print(
        f"Median parallel latency    : "
        f"{parallel_median:.3f} seconds"
    )

    # ========================================================
    # SPEEDUP
    # ========================================================

    speedup = (
        sequential_average
        / parallel_average
    )

    print(
        f"\nSpeedup                    : "
        f"{speedup:.2f}x"
    )

    print("\n")
    print("=" * 70)
    print("BENCHMARK COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())

import asyncio

from app.async_tools import (
    run_tools_sequential,
    run_tools_parallel,
)


async def main():

    query = "What are the rules for professional conduct?"

    print("=" * 70)
    print("ASYNC TOOL TEST")
    print("=" * 70)

    print("\nRunning sequential version...")

    sequential = await run_tools_sequential(query)

    print(
        f"Sequential latency: "
        f"{sequential['latency']:.3f} seconds"
    )

    print("\nRunning parallel version...")

    parallel = await run_tools_parallel(query)

    print(
        f"Parallel latency: "
        f"{parallel['latency']:.3f} seconds"
    )


if __name__ == "__main__":
    asyncio.run(main())


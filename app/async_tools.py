
import asyncio
import time

from app.retrieval import search_documents

# ============================================================
# SYNC TOOL
# ============================================================

def search_policy_sync(query):
    """
    Existing synchronous Chroma retrieval.
    """

    results = search_documents(
        query,
        k=3
    )

    formatted_results = []

    for doc, score in results:

        formatted_results.append(
            {
                "document": doc,
                "score": score
            }
        )

    return formatted_results


# ============================================================
# ASYNC WRAPPER
# ============================================================

async def search_policy(query):
    """
    Run the synchronous Chroma operation
    in a background thread.
    """

    return await asyncio.to_thread(
        search_policy_sync,
        query
    )


# ============================================================
# SPECIALIZED TOOLS
# ============================================================

async def search_hr_policy(query):

    return await asyncio.to_thread(
        search_policy_sync,
        f"HR policy {query}"
    )


async def search_it_policy(query):

    return await asyncio.to_thread(
        search_policy_sync,
        f"IT policy {query}"
    )


async def search_company_policy(query):

    return await asyncio.to_thread(
        search_policy_sync,
        f"company corporate policy {query}"
    )


# ============================================================
# SEQUENTIAL VERSION
# ============================================================

async def run_tools_sequential(query):

    start = time.perf_counter()

    hr_results = await search_hr_policy(query)

    it_results = await search_it_policy(query)

    company_results = await search_company_policy(query)

    latency = time.perf_counter() - start

    return {
        "hr_policy": hr_results,
        "it_policy": it_results,
        "company_policy": company_results,
        "latency": latency
    }


# ============================================================
# PARALLEL VERSION
# ============================================================

async def run_tools_parallel(query):

    start = time.perf_counter()

    (
        hr_results,
        it_results,
        company_results
    ) = await asyncio.gather(

        search_hr_policy(query),

        search_it_policy(query),

        search_company_policy(query)
    )

    latency = time.perf_counter() - start

    return {
        "hr_policy": hr_results,
        "it_policy": it_results,
        "company_policy": company_results,
        "latency": latency
    }


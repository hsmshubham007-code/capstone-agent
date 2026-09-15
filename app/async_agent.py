import asyncio
import time

from app.async_tools import run_tools_parallel
from app.llm import MODEL, client


def format_context(tool_results):
    """
    Convert retrieved documents into a single context string.
    """

    sections = []

    for tool_name, result in tool_results.items():

        # latency is metadata, not retrieval results
        if tool_name == "latency":
            continue

        sections.append(
            f"\n===== {tool_name} ====="
        )

        for item in result:

            doc = item["document"]
            score = item["score"]

            source = doc.metadata.get(
                "source",
                "Unknown"
            )

            page = doc.metadata.get(
                "page",
                "Unknown"
            )

            sections.append(
                f"""
Source: {source}
Page: {page}
Similarity score: {score:.4f}

{doc.page_content}
"""
            )

    return "\n".join(sections)


async def generate_answer_async(question, context):
    """
    Run the synchronous Groq client in a background thread.
    """

    prompt = f"""
You are a company policy assistant.

Answer the user's question using ONLY the provided context.

Rules:
- Give a complete answer based on all relevant information.
- Do not add information that is not present in the context.
- If multiple relevant points are present, include them.
- If the answer is not present in the context, say:
"I don't have enough information in the provided documents."

Context:
{context}

Question:
{question}

Answer:
"""

    def call_llm():

        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0
        )

        return response.choices[0].message.content

    return await asyncio.to_thread(call_llm)


async def async_agent(question):
    """
    Complete asynchronous capstone flow:

    1. Run HR, IT and company retrieval in parallel.
    2. Combine retrieved context.
    3. Call Groq asynchronously.
    4. Return latency measurements.
    5. Return a clean hierarchy of tools used.
    6. Return all cited sources.
    """

    total_start = time.perf_counter()

    # =====================================================
    # PARALLEL RETRIEVAL
    # =====================================================

    tool_start = time.perf_counter()

    tool_results = await run_tools_parallel(question)

    tool_latency = time.perf_counter() - tool_start

    # =====================================================
    # BUILD CONTEXT
    # =====================================================

    context = format_context(tool_results)

    # =====================================================
    # GROQ LLM
    # =====================================================

    llm_start = time.perf_counter()

    answer = await generate_answer_async(
        question,
        context
    )

    llm_latency = time.perf_counter() - llm_start

    # =====================================================
    # TOTAL LATENCY
    # =====================================================

    total_latency = time.perf_counter() - total_start

    # =====================================================
    # TOOLS USED
    # =====================================================

    tools = {
        "search_documents": [
            "HR Policy Search",
            "IT Policy Search",
            "Company Policy Search"
        ]
    }

    # =====================================================
    # SOURCES
    # =====================================================

    sources = []

    for tool_name, results in tool_results.items():

        # latency is metadata, not a tool result
        if tool_name == "latency":
            continue

        for item in results:

            doc = item["document"]

            source = {
                "tool": tool_name,
                "source": doc.metadata.get(
                    "source",
                    "Unknown"
                ),
                "page": doc.metadata.get(
                    "page",
                    "Unknown"
                ),
                "score": item["score"]
            }

            sources.append(source)

    # =====================================================
    # RETURN RESULT
    # =====================================================

    return {
        "question": question,
        "answer": answer,

        "tool_latency": tool_latency,
        "llm_latency": llm_latency,
        "total_latency": total_latency,

        "tools": tools,

        "sources": sources
    }


async def main():

    question = input(
        "Ask a company policy question: "
    )

    print("\nRunning asynchronous agent...")
    print("=" * 70)

    result = await async_agent(question)

    # =====================================================
    # ANSWER
    # =====================================================

    print("\nANSWER")
    print("-" * 70)

    print(result["answer"])

    # =====================================================
    # TOOLS
    # =====================================================

    print("\nTOOLS USED")
    print("-" * 70)

    for tool, branches in result["tools"].items():

        print(f"- {tool}")

        for branch in branches:

            print(f"    └── {branch}")

    # =====================================================
    # SOURCES
    # =====================================================

    print("\nSOURCES")
    print("-" * 70)

    for source in result["sources"]:

        print(
            f"- {source['source']} "
            f"(page {source['page']}) "
            f"[score={source['score']:.4f}]"
        )

    # =====================================================
    # LATENCY
    # =====================================================

    print("\nLATENCY")
    print("-" * 70)

    print(
        f"Parallel retrieval: "
        f"{result['tool_latency']:.3f} seconds"
    )

    print(
        f"Groq LLM: "
        f"{result['llm_latency']:.3f} seconds"
    )

    print(
        f"Total: "
        f"{result['total_latency']:.3f} seconds"
    )


if __name__ == "__main__":
    asyncio.run(main())


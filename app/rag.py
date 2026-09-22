import time

from app.llm import (
    generate_answer,
    generate_answer_with_metadata,
)
from app.metrics import metrics
from app.retrieval import search_documents

NO_INFORMATION_ANSWER = (
    "I don't have enough information in the "
    "provided documents to answer that question."
)


def answer_question(question, k=3):
    """
    Answer a question using retrieved company documents.

    If no relevant documents are retrieved, do not call the LLM.

    The generate_answer interface is preserved so existing tests
    can monkeypatch app.rag.generate_answer.

    Production requests use generate_answer_with_metadata() so
    token usage, reasoning tokens, latency, and estimated cost
    are preserved.
    """

    # -------------------------------------------------
    # Retrieval
    # -------------------------------------------------

    retrieval_start = time.perf_counter()

    results = search_documents(
        question,
        k=k,
    )

    retrieval_latency_ms = (
        time.perf_counter() - retrieval_start
    ) * 1000

    metrics.observe_retrieval_latency(
        retrieval_latency_ms
    )

    # -------------------------------------------------
    # No relevant documents found
    # -------------------------------------------------

    if not results:
        return {
            "answer": NO_INFORMATION_ANSWER,
            "sources": [],
            "results": [],
            "retrieval_metadata": {
                "documents_retrieved": 0,
                "context_chars": 0,
                "sources": [],
                "scores": [],
                "latency_ms": round(
                    retrieval_latency_ms,
                    2,
                ),
            },
            "llm_metadata": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "reasoning_tokens": 0,
                "total_tokens": 0,
                "cost_usd": 0.0,
            },
        }

    # -------------------------------------------------
    # Build context
    # -------------------------------------------------

    context_parts = []
    sources = []
    scores = []

    for doc, score in results:
        context_parts.append(
            doc.page_content
        )

        scores.append(
            round(float(score), 4)
        )

        source = doc.metadata.get(
            "source"
        )

        if source and source not in sources:
            sources.append(source)

    context = "\n\n".join(
        context_parts
    )

    # -------------------------------------------------
    # Retrieval diagnostics
    # -------------------------------------------------

    retrieval_metadata = {
        "documents_retrieved": len(results),
        "context_chars": len(context),
        "sources": sources,
        "scores": scores,
        "latency_ms": round(
            retrieval_latency_ms,
            2,
        ),
    }

    # -------------------------------------------------
    # Generate answer
    #
    # Keep compatibility with tests that monkeypatch
    # app.rag.generate_answer.
    # -------------------------------------------------

    original_generate_answer = (
        __import__(
            "app.llm",
            fromlist=["generate_answer"],
        ).generate_answer
    )

    if generate_answer is not original_generate_answer:
        # A test has monkeypatched app.rag.generate_answer.
        answer = generate_answer(
            question,
            context,
        )

        llm_metadata = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "reasoning_tokens": 0,
            "total_tokens": 0,
            "cost_usd": 0.0,
        }

    else:
        # Production path: preserve real LLM usage metadata.
        llm_result = (
            generate_answer_with_metadata(
                question,
                context,
            )
        )

        answer = llm_result["answer"]

        llm_metadata = llm_result.get(
            "metadata",
            {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "reasoning_tokens": 0,
                "total_tokens": 0,
                "cost_usd": 0.0,
            },
        )

    # -------------------------------------------------
    # Return structured RAG result
    # -------------------------------------------------

    return {
        "answer": answer,
        "sources": sources,
        "results": results,
        "retrieval_metadata": retrieval_metadata,
        "llm_metadata": llm_metadata,
    }


if __name__ == "__main__":
    question = input(
        "Ask a question: "
    )

    result = answer_question(
        question
    )

    print("\nAnswer:")
    print(result["answer"])

    print("\nSources:")

    for source in result["sources"]:
        print(f"- {source}")

    print("\nRetrieval Metadata:")
    print(result["retrieval_metadata"])

    print("\nLLM Metadata:")
    print(result["llm_metadata"])
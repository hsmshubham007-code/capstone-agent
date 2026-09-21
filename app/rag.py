from app.llm import generate_answer
from app.retrieval import search_documents

NO_INFORMATION_ANSWER = (
    "I don't have enough information in the "
    "provided documents to answer that question."
)


def answer_question(question, k=3):
    """
    Answer a question using retrieved company documents.

    If no relevant documents are retrieved, do not call the LLM.
    Return an honest limitation instead.

    The existing generate_answer() interface is preserved so
    existing tests can monkeypatch app.rag.generate_answer.
    """

    results = search_documents(
        question,
        k=k,
    )

    # -------------------------------------------------
    # No relevant documents found
    # -------------------------------------------------

    if not results:
        return {
            "answer": NO_INFORMATION_ANSWER,
            "sources": [],
            "results": [],
            "llm_metadata": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
                "cost_usd": 0.0,
            },
        }

    # -------------------------------------------------
    # Build context
    # -------------------------------------------------

    context_parts = []
    sources = []

    for doc, score in results:
        context_parts.append(doc.page_content)

        source = doc.metadata.get("source")

        if source and source not in sources:
            sources.append(source)

    context = "\n\n".join(context_parts)

    # -------------------------------------------------
    # Generate answer
    # -------------------------------------------------

    answer = generate_answer(
        question,
        context,
    )

    return {
        "answer": answer,
        "sources": sources,
        "results": results,
        "llm_metadata": {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "cost_usd": 0.0,
        },
    }


if __name__ == "__main__":
    question = input("Ask a question: ")

    result = answer_question(question)

    print("\nAnswer:")
    print(result["answer"])

    print("\nSources:")

    for source in result["sources"]:
        print(f"- {source}")
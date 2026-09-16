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
        }

    # -------------------------------------------------
    # Build context from retrieved documents
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
    # Generate answer using retrieved context
    # -------------------------------------------------

    answer = generate_answer(
        question,
        context,
    )

    return {
        "answer": answer,
        "sources": sources,
        "results": results,
    }


if __name__ == "__main__":
    question = input("Ask a question: ")

    result = answer_question(question)

    print("\nAnswer:")
    print(result["answer"])

    print("\nSources:")

    for source in result["sources"]:
        print(f"- {source}")
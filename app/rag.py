from app.retrieval import search_documents
from app.llm import generate_answer


def answer_question(question, k=3):
    results = search_documents(question, k=k)

    context_parts = []
    sources = []

    for doc, score in results:
        context_parts.append(doc.page_content)

        source = doc.metadata.get("source")

        if source and source not in sources:
            sources.append(source)

    context = "\n\n".join(context_parts)

    answer = generate_answer(question, context)

    return {
        "answer": answer,
        "sources": sources,
        "results": results
    }


if __name__ == "__main__":
    question = input("Ask a question: ")

    result = answer_question(question)

    print("\nAnswer:")
    print(result["answer"])

    print("\nSources:")

    for source in result["sources"]:
        print(f"- {source}")
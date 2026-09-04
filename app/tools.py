from app.rag import answer_question

def search_documents_tool(question, history=None):
    from app.context import build_contextual_query

    history = history or []

    contextual_query = build_contextual_query(
        question,
        history
    )

    result = answer_question(contextual_query)

    return {
    "name": "search_documents",
    "answer": result["answer"],
    "sources": result["sources"],
    "results": [
        {
            "source": doc.metadata.get("source"),
            "score": score,
            "content": doc.page_content[:300]
        }
        for doc, score in result["results"]
    ]
}
    
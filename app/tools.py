from app.audit import (
    record_tool_call,
)
from app.rag import answer_question


def search_documents_tool(
    question,
    history=None,
    request_id=None,
):
    """
    Search the company policy documents.

    This is a READ-ONLY tool, so it does not require approval.

    Every execution is recorded in the audit trail.

    The result includes:
    - answer
    - sources
    - retrieval metadata
    - LLM metadata
    - retrieved document previews
    """

    from app.context import (
        build_contextual_query,
    )

    history = history or []

    if request_id:
        record_tool_call(
            request_id=request_id,
            tool_name="search_documents",
            arguments={
                "question": question,
            },
            status="STARTED",
        )

    try:
        contextual_query = (
            build_contextual_query(
                question,
                history,
            )
        )

        result = answer_question(
            contextual_query
        )

        output = {
            "name": "search_documents",

            "answer": result["answer"],

            "sources": result["sources"],

            "retrieval_metadata": result.get(
                "retrieval_metadata"
            ),

            "llm_metadata": result.get(
                "llm_metadata"
            ),

            "results": [
                {
                    "source": doc.metadata.get(
                        "source"
                    ),
                    "score": score,
                    "content": (
                        doc.page_content[:300]
                    ),
                }
                for doc, score in result[
                    "results"
                ]
            ],
        }

        if request_id:
            record_tool_call(
                request_id=request_id,
                tool_name="search_documents",
                arguments={
                    "question": question,
                },
                status="SUCCESS",
                outcome={
                    "sources_count": len(
                        output["sources"]
                    ),
                    "results_count": len(
                        output["results"]
                    ),
                },
            )

        return output

    except Exception as error:
        if request_id:
            record_tool_call(
                request_id=request_id,
                tool_name="search_documents",
                arguments={
                    "question": question,
                },
                status="FAILED",
                error=str(error),
            )

        raise
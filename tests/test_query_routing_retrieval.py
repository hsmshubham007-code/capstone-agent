from app.retrieval import search_documents
from app.router import decide_tool


def test_policy_query_retrieves_documents():
    results = search_documents(
        "What is the company leave policy?"
    )

    assert len(results) > 0

    for doc, score in results:
        assert score <= 1.10


def test_policy_query_routes_to_search():
    tool = decide_tool(
        "What is the company leave policy?"
    )

    assert tool == "search_documents"


def test_stock_query_does_not_use_rag():
    tool = decide_tool(
        "What is the company's stock price today?"
    )

    assert tool == "no_tool"


def test_password_query_routes_to_search():
    tool = decide_tool(
        "What is the company password policy?"
    )

    assert tool == "search_documents"
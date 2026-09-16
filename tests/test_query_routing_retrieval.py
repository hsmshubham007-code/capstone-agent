from app.agent import run_agent
from app.retrieval import search_documents


def test_policy_query_retrieves_documents():
    results = search_documents(
        "What is the company leave policy?"
    )

    assert len(results) > 0

    for doc, score in results:
        assert score <= 1.0
        assert doc.metadata.get("source")


def test_unknown_policy_has_no_relevant_results():
    results = search_documents(
        "What is the company relocation allowance policy?"
    )

    assert results == []


def test_unknown_policy_does_not_hallucinate():
    result = run_agent(
        "What is the company relocation allowance policy?",
        "test-unknown-policy",
    )

    assert result["tool"] == "search_documents"
    assert result["sources"] == []

    assert (
        "I don't have enough information"
        in result["answer"]
    )

    search_trace = next(
        item
        for item in result["trace"]
        if item["step"] == "search_documents"
    )

    assert (
        search_trace["retrieval_status"]
        == "NO_RELEVANT_RESULTS"
    )


def test_general_question_does_not_search_documents():
    result = run_agent(
        "What is Python?",
        "test-general-question",
    )

    assert result["tool"] == "no_tool"
    assert result["sources"] == []
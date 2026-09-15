from app.rag import answer_question
from app.retrieval import search_documents


def test_relevant_question():
    results = search_documents(
        "What does the company say about professional conduct?"
    )

    assert len(results) > 0


def test_irrelevant_question():
    results = search_documents(
        "What is the company's stock price today?"
    )

    assert len(results) == 0


def test_relevant_sources():
    result = answer_question(
        "What does the company say about professional conduct?"
    )

    assert len(result["sources"]) > 0
    assert "company_policy.pdf" in result["sources"] or \
           "hr_policy.pdf" in result["sources"]


def test_no_sources_for_irrelevant_question():
    result = answer_question(
        "What is the company's stock price today?"
    )

    assert result["sources"] == []


def test_no_hallucination():
    result = answer_question(
        "What is the company's stock price today?"
    )

    assert "I don't have enough information" in result["answer"]
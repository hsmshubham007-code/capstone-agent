from types import SimpleNamespace

from app import rag, retrieval


def fake_documents(question, k=3):
    if "professional conduct" in question.lower():
        return [
            SimpleNamespace(
                page_content=(
                    "The company expects professional conduct, "
                    "respect, honesty, transparency, confidentiality, "
                    "and compliance with applicable laws."
                ),
                metadata={
                    "source": "company_policy.pdf"
                },
            ),
            SimpleNamespace(
                page_content=(
                    "Employees must behave professionally and "
                    "treat colleagues with respect."
                ),
                metadata={
                    "source": "hr_policy.pdf"
                },
            ),
        ]

    return []


def test_relevant_question(monkeypatch):
    monkeypatch.setattr(
        retrieval,
        "search_documents",
        fake_documents,
    )

    results = retrieval.search_documents(
        "What does the company say about professional conduct?"
    )

    assert len(results) > 0


def test_irrelevant_question(monkeypatch):
    monkeypatch.setattr(
        retrieval,
        "search_documents",
        fake_documents,
    )

    results = retrieval.search_documents(
        "What is the company's stock price today?"
    )

    assert len(results) == 0


def test_relevant_sources(monkeypatch):
    fake_results = [
        (
            SimpleNamespace(
                page_content="Professional conduct policy.",
                metadata={
                    "source": "company_policy.pdf"
                },
            ),
            0.1,
        )
    ]

    monkeypatch.setattr(
        rag,
        "search_documents",
        lambda question, k=3: fake_results,
    )

    monkeypatch.setattr(
        rag,
        "generate_answer",
        lambda question, context: (
            "The company expects professional conduct, "
            "respect, honesty, transparency, and confidentiality."
        ),
    )

    result = rag.answer_question(
        "What does the company say about professional conduct?"
    )

    assert len(result["sources"]) > 0

    assert (
        "company_policy.pdf" in result["sources"]
        or "hr_policy.pdf" in result["sources"]
    )


def test_no_sources_for_irrelevant_question(monkeypatch):
    monkeypatch.setattr(
        rag,
        "search_documents",
        lambda question, k=3: [],
    )

    result = rag.answer_question(
        "What is the company's stock price today?"
    )

    assert result["sources"] == []


def test_no_hallucination(monkeypatch):
    monkeypatch.setattr(
        rag,
        "search_documents",
        lambda question, k=3: [],
    )

    result = rag.answer_question(
        "What is the company's stock price today?"
    )

    assert "I don't have enough information" in result["answer"]
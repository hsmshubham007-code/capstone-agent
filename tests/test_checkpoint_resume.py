from app.graph import graph


def test_checkpoint_resume(monkeypatch):
    def fake_search_documents_tool(
        question,
        history=None,
        request_id=None,
    ):
        return {
            "name": "search_documents",
            "answer": (
                "The company expects professional conduct, "
                "respect, honesty, transparency, confidentiality, "
                "and compliance with applicable policies."
            ),
            "sources": ["company_policy.pdf"],
            "results": [
                {
                    "source": "company_policy.pdf",
                    "score": 0.1,
                    "content": "Professional conduct policy.",
                }
            ],
        }

    monkeypatch.setattr(
        "app.tools.search_documents_tool",
        fake_search_documents_tool,
    )

    thread_id = "resume-test-001"

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    initial_state = {
        "session_id": thread_id,
        "question": "What are the rules for professional conduct?",
        "conversation_history": [],
        "tool": "",
        "answer": "",
        "sources": [],
        "tools_used": [],
        "trace": [],
    }

    result = graph.invoke(
        initial_state,
        config=config,
    )

    assert result["answer"]

    checkpoint = graph.get_state(config)

    assert (
        checkpoint.config["configurable"]["thread_id"]
        == thread_id
    )

    assert checkpoint.values["question"] == (
        "What are the rules for professional conduct?"
    )

    assert checkpoint.values["answer"]
    assert checkpoint.values["sources"]
    assert checkpoint.values["trace"]

    resumed_checkpoint = graph.get_state(config)

    assert (
        resumed_checkpoint.values["answer"]
        == checkpoint.values["answer"]
    )
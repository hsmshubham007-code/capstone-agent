import pytest

from app.graph import graph


@pytest.fixture
def checkpoint_state():
    return {
        "session_id": "checkpoint-test",
        "question": "What are the rules for professional conduct?",
        "conversation_history": [],
        "tool": "",
        "answer": "",
        "sources": [],
        "tools_used": [],
        "trace": [],
    }


def test_durable_checkpointing(checkpoint_state, monkeypatch):
    def fake_generate_answer(question, context):
        return (
            "The company expects professional conduct, "
            "respect, honesty, transparency, confidentiality, "
            "and compliance with applicable policies."
        )

    monkeypatch.setattr(
        "app.rag.generate_answer",
        fake_generate_answer,
    )

    config = {
        "configurable": {
            "thread_id": "demo-thread-001"
        }
    }

    result = graph.invoke(
        checkpoint_state,
        config=config,
    )

    assert result["answer"]
    assert "search_documents" in result["tools_used"]

    checkpoint = graph.get_state(config)

    assert (
        checkpoint.config["configurable"]["thread_id"]
        == "demo-thread-001"
    )

    assert checkpoint.values["question"] == (
        "What are the rules for professional conduct?"
    )

    assert checkpoint.values["answer"]
    assert checkpoint.values["sources"]
    assert checkpoint.values["trace"]
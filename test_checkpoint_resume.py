
from app.graph import graph


def test_checkpoint_resume(monkeypatch):
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

    # First execution
    result = graph.invoke(
        initial_state,
        config=config,
    )

    assert result["answer"]

    # Read persisted checkpoint
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

    # Verify state can be read again from the same thread.
    resumed_checkpoint = graph.get_state(config)

    assert resumed_checkpoint.values["answer"] == (
        checkpoint.values["answer"]
    )
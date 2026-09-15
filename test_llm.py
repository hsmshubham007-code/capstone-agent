from app import llm


def test_generate_answer(monkeypatch):
    class FakeMessage:
        content = (
            "The company expects professional conduct, "
            "respect, honesty, transparency, and "
            "confidentiality."
        )

    class FakeChoice:
        def __init__(self):
            self.message = FakeMessage()

    class FakeUsage:
        prompt_tokens = 10
        completion_tokens = 15
        total_tokens = 25

    class FakeResponse:
        def __init__(self):
            self.choices = [FakeChoice()]
            self.usage = FakeUsage()

    class FakeCompletions:
        def create(self, **kwargs):
            return FakeResponse()

    class FakeChat:
        def __init__(self):
            self.completions = FakeCompletions()

    class FakeClient:
        def __init__(self):
            self.chat = FakeChat()

    monkeypatch.setattr(
        llm,
        "get_client",
        lambda: FakeClient(),
    )

    answer = llm.generate_answer(
        "What does the company expect regarding professional conduct?",
        """
        TechNova Solutions Pvt. Ltd. expects everyone representing
        the company to:
        - Act professionally.
        - Treat others with respect.
        - Be honest and transparent.
        - Protect company interests.
        - Follow applicable laws.
        - Maintain confidentiality.
        """,
    )

    assert answer
    assert "professional conduct" in answer.lower()
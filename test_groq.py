import os

import pytest
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
model = os.getenv("GROQ_MODEL")

if not api_key or not model:
    pytest.skip(
        "GROQ_API_KEY/GROQ_MODEL not configured; "
        "skipping live Groq integration test.",
        allow_module_level=True,
    )


def test_groq_connection():
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1",
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": (
                    "Explain what an AI agent is "
                    "in one sentence."
                ),
            }
        ],
    )

    assert response.choices
    assert response.choices[0].message.content
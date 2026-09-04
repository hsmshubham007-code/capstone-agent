from app.llm import generate

messages = [
    {
        "role": "user",
        "content": "Reply with exactly: Groq connection successful"
    }
]

print(generate(messages))
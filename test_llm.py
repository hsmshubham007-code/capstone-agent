from app.llm import generate_answer

context = """
TechNova Solutions Pvt. Ltd. expects everyone representing the company to:
- Act professionally.
- Treat others with respect.
- Be honest and transparent.
- Protect company interests.
- Follow applicable laws.
- Maintain confidentiality.
"""

question = "What does the company expect regarding professional conduct?"

answer = generate_answer(question, context)

print("\nAnswer:")
print(answer)
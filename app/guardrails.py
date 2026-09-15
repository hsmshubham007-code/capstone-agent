import re

MAX_INPUT_LENGTH = 2000


def validate_input(question):
    if not isinstance(question, str):
        raise TypeError("Question must be a string.")

    question = question.strip()

    if not question:
        raise ValueError("Question cannot be empty.")

    if len(question) > MAX_INPUT_LENGTH:
        raise ValueError("Question is too long.")

    return question


def detect_prompt_injection(question):
    patterns = [
        r"ignore previous instructions",
        r"ignore all previous instructions",
        r"forget your instructions",
        r"system prompt",
        r"reveal your prompt",
        r"show me your instructions",
        r"disregard previous instructions",
    ]

    question_lower = question.lower()

    for pattern in patterns:
        if re.search(pattern, question_lower):
            return True

    return False


def validate_output(answer):
    if not isinstance(answer, str):
        raise TypeError("Agent output must be a string.")

    answer = answer.strip()

    if not answer:
        raise ValueError("Agent returned an empty answer.")

    return answer
import re

MAX_INPUT_LENGTH = 2000


PROMPT_INJECTION_PATTERNS = [
    # Instruction override
    r"\bignore\b.{0,80}\b(previous|prior|original|earlier)\b.{0,40}\binstructions?\b",
    r"\bignore\b.{0,80}\ball\b.{0,40}\binstructions?\b",
    r"\bdisregard\b.{0,80}\b(previous|prior|original|earlier)\b.{0,40}\binstructions?\b",
    r"\bforget\b.{0,80}\b(previous|prior|original|original)\b.{0,40}\binstructions?\b",
    r"\bforget\b.{0,80}\byour\b.{0,40}\binstructions?\b",

    # Safety/policy bypass
    r"\bignore\b.{0,80}\bsafety\b.{0,40}\brules?\b",
    r"\bdisregard\b.{0,80}\bsafety\b.{0,40}\brules?\b",
    r"\bbypass\b.{0,80}\b(safety|security|policy|policies)\b",
    r"\boverride\b.{0,80}\b(safety|security|policy|policies|rules?)\b",

    # Role/persona hijacking
    r"\byou are now\b.{0,100}\b(unrestricted|unfiltered|evil|jailbroken)\b",
    r"\bact as\b.{0,100}\b(unrestricted|unfiltered|jailbroken)\b",
    r"\bpretend\b.{0,100}\byou have no\b.{0,50}\brestrictions?\b",
    r"\bfrom now on\b.{0,100}\b(without restrictions|without limits)\b",

    # System prompt / hidden instruction extraction
    r"\bsystem\s+prompt\b",
    r"\breveal\b.{0,80}\b(system|hidden|secret)\b.{0,50}\b(prompt|instructions?)\b",
    r"\bshow\b.{0,80}\b(system|hidden|secret)\b.{0,50}\b(prompt|instructions?)\b",
    r"\bprint\b.{0,80}\b(system|hidden|secret)\b.{0,50}\b(prompt|instructions?)\b",
    r"\bextract\b.{0,80}\b(system|hidden|secret)\b.{0,50}\b(prompt|instructions?)\b",

    # Direct instruction disclosure
    r"\breveal\b.{0,80}\byour\b.{0,50}\binstructions?\b",
    r"\bshow\s+me\b.{0,80}\byour\b.{0,50}\binstructions?\b",
    r"\bprint\b.{0,80}\byour\b.{0,50}\binstructions?\b",

    # Jailbreak terminology
    r"\bjailbreak\b",
    r"\bdeveloper\s+message\b",
    r"\bhidden\s+instructions?\b",
    r"\bsecret\s+instructions?\b",
]


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
    if not isinstance(question, str):
        return False

    question_lower = question.lower()

    for pattern in PROMPT_INJECTION_PATTERNS:
        if re.search(
            pattern,
            question_lower,
            flags=re.IGNORECASE,
        ):
            return True

    return False


def validate_output(answer):
    if not isinstance(answer, str):
        raise TypeError("Agent output must be a string.")

    answer = answer.strip()

    if not answer:
        raise ValueError("Agent returned an empty answer.")

    return answer
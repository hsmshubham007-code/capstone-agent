import logging
import os
import time

from dotenv import load_dotenv
from openai import OpenAI

from app.metrics import metrics

# =========================================================
# Configuration
# =========================================================

load_dotenv()

logger = logging.getLogger("company-policy-agent.llm")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL = os.getenv("GROQ_MODEL")
GROQ_BASE_URL = "https://api.groq.com/openai/v1"


# =========================================================
# Custom exception
# =========================================================


class LLMServiceError(Exception):
    """Raised when the Groq LLM cannot generate an answer."""


# =========================================================
# Groq client
# =========================================================


def get_client():
    """
    Create the Groq OpenAI-compatible client lazily.

    The client is created only when an LLM request is made.
    This allows tests and CI to import the module without
    requiring GROQ_API_KEY.
    """

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise LLMServiceError(
            "GROQ_API_KEY is missing."
        )

    return OpenAI(
        api_key=api_key,
        base_url=GROQ_BASE_URL,
    )


# =========================================================
# LLM generation
# =========================================================


def generate_answer(
    question,
    context,
):
    """
    Generate an answer using the Groq LLM.

    Monitoring recorded:
    - request count
    - latency
    - prompt tokens
    - completion tokens
    - total tokens
    - errors
    """

    prompt = f"""
You are a company policy assistant.

Answer the user's question using ONLY the provided context.

Rules:
- Give a complete answer based on all relevant information in the context.
- Do not add information that is not present in the context.
- If multiple relevant points are present, include them.
- Do not invent company policies.
- Do not use outside knowledge.
- If the answer is not present in the context, say:
"I don't have enough information in the provided documents."

Context:
{context}

Question:
{question}

Answer:
"""

    # -----------------------------------------------------
    # Validate configuration
    # -----------------------------------------------------

    api_key = os.getenv("GROQ_API_KEY")
    model = os.getenv("GROQ_MODEL")

    if not api_key:
        metrics.increment(
            "llm_configuration_errors_total"
        )

        logger.error(
            "GROQ_API_KEY is not configured"
        )

        raise LLMServiceError(
            "The Groq API key is not configured."
        )

    if not model:
        metrics.increment(
            "llm_configuration_errors_total"
        )

        logger.error(
            "GROQ_MODEL is not configured"
        )

        raise LLMServiceError(
            "The Groq model is not configured."
        )

    # -----------------------------------------------------
    # Start monitoring
    # -----------------------------------------------------

    metrics.increment(
        "llm_requests_total"
    )

    start_time = time.perf_counter()

    try:
        # -------------------------------------------------
        # Create client lazily
        # -------------------------------------------------

        client = get_client()

        # -------------------------------------------------
        # Groq API call
        # -------------------------------------------------

        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            temperature=0,
        )

        # -------------------------------------------------
        # Calculate latency
        # -------------------------------------------------

        latency_ms = (
            time.perf_counter() - start_time
        ) * 1000

        # -------------------------------------------------
        # Token usage
        # -------------------------------------------------

        usage = getattr(
            response,
            "usage",
            None,
        )

        prompt_tokens = 0
        completion_tokens = 0
        total_tokens = 0

        if usage:
            prompt_tokens = (
                getattr(
                    usage,
                    "prompt_tokens",
                    0,
                )
                or 0
            )

            completion_tokens = (
                getattr(
                    usage,
                    "completion_tokens",
                    0,
                )
                or 0
            )

            total_tokens = (
                getattr(
                    usage,
                    "total_tokens",
                    0,
                )
                or 0
            )

        metrics.record_llm_usage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
        )

        # -------------------------------------------------
        # Extract answer
        # -------------------------------------------------

        answer = (
            response
            .choices[0]
            .message
            .content
        )

        if not answer or not answer.strip():
            metrics.increment(
                "llm_empty_response_total"
            )

            metrics.observe_latency(
                latency_ms
            )

            logger.error(
                "Groq LLM returned an empty response",
                extra={
                    "model": model,
                    "latency_ms": round(
                        latency_ms,
                        2,
                    ),
                },
            )

            raise LLMServiceError(
                "The Groq LLM returned an empty response."
            )

        # -------------------------------------------------
        # Successful request
        # -------------------------------------------------

        metrics.observe_latency(
            latency_ms
        )

        metrics.increment(
            "llm_requests_success_total"
        )

        logger.info(
            "LLM request completed",
            extra={
                "model": model,
                "latency_ms": round(
                    latency_ms,
                    2,
                ),
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
            },
        )

        return answer.strip()

    except LLMServiceError:
        raise

    except Exception as exc:
        latency_ms = (
            time.perf_counter() - start_time
        ) * 1000

        metrics.increment(
            "llm_errors_total"
        )

        metrics.observe_latency(
            latency_ms
        )

        logger.exception(
            "LLM request failed",
            extra={
                "model": model,
                "latency_ms": round(
                    latency_ms,
                    2,
                ),
                "error": str(exc),
            },
        )

        raise LLMServiceError(
            "The Groq LLM service is currently unavailable."
        ) from exc
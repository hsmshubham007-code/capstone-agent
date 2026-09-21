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

logger = logging.getLogger(
    "company-policy-agent.llm"
)

GROQ_BASE_URL = (
    "https://api.groq.com/openai/v1"
)


# =========================================================
# Custom exception
# =========================================================

class LLMServiceError(Exception):
    """
    Raised when the Groq LLM cannot generate
    an answer.
    """


# =========================================================
# Runtime configuration
# =========================================================

def get_api_key():
    """
    Read the Groq API key at runtime.
    """
    return os.getenv("GROQ_API_KEY")


def get_model():
    """
    Read the Groq model at runtime.
    """
    return os.getenv("GROQ_MODEL")


# =========================================================
# Groq client
# =========================================================

def get_client():
    api_key = get_api_key()

    if not api_key:
        raise LLMServiceError(
            "GROQ_API_KEY is missing."
        )

    return OpenAI(
        api_key=api_key,
        base_url=GROQ_BASE_URL,
    )


# =========================================================
# Cost calculation
# =========================================================

def calculate_cost(
    model,
    prompt_tokens,
    completion_tokens,
):
    """
    Calculate estimated Groq API cost.

    Prices are USD per 1 million tokens.
    """

    pricing = {
        "openai/gpt-oss-20b": {
            "input": 0.075,
            "output": 0.30,
        },
        "openai/gpt-oss-120b": {
            "input": 0.15,
            "output": 0.60,
        },
        "openai/gpt-oss-safeguard-20b": {
            "input": 0.075,
            "output": 0.30,
        },
    }

    model_price = pricing.get(model)

    if model_price is None:
        logger.warning(
            "No pricing configured for model: %s",
            model,
        )
        return 0.0

    input_cost = (
        prompt_tokens / 1_000_000
    ) * model_price["input"]

    output_cost = (
        completion_tokens / 1_000_000
    ) * model_price["output"]

    return input_cost + output_cost


# =========================================================
# LLM generation with metadata
# =========================================================

def generate_answer_with_metadata(
    question,
    context,
):
    """
    Generate an answer using the Groq LLM.

    Returns both the answer and per-request
    monitoring metadata.

    Metadata includes:
    - model
    - latency
    - prompt tokens
    - completion tokens
    - total tokens
    - estimated cost
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

    api_key = get_api_key()
    model = get_model()

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

    metrics.increment(
        "llm_requests_total"
    )

    start_time = time.perf_counter()

    try:
        client = get_client()

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

        latency_ms = (
            time.perf_counter()
            - start_time
        ) * 1000

        usage = getattr(
            response,
            "usage",
            None,
        )

        prompt_tokens = 0
        completion_tokens = 0
        total_tokens = 0

        if usage:
            prompt_tokens = getattr(
                usage,
                "prompt_tokens",
                0,
            ) or 0

            completion_tokens = getattr(
                usage,
                "completion_tokens",
                0,
            ) or 0

            total_tokens = getattr(
                usage,
                "total_tokens",
                0,
            ) or 0

        metrics.observe_latency(
            latency_ms
        )

        metrics.record_llm_usage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
        )

        cost_usd = calculate_cost(
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
        )

        metrics.record_cost(
            cost_usd
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
                "completion_tokens": (
                    completion_tokens
                ),
                "total_tokens": total_tokens,
                "cost_usd": round(
                    cost_usd,
                    8,
                ),
            },
        )

        answer = (
            response
            .choices[0]
            .message
            .content
        )

        if not answer:
            metrics.increment(
                "llm_empty_response_total"
            )

            raise LLMServiceError(
                "The Groq LLM returned an empty response."
            )

        return {
            "answer": answer.strip(),
            "metadata": {
                "model": model,
                "latency_ms": round(
                    latency_ms,
                    2,
                ),
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
                "cost_usd": round(
                    cost_usd,
                    8,
                ),
            },
        }

    except LLMServiceError:
        raise

    except Exception as exc:
        latency_ms = (
            time.perf_counter()
            - start_time
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


# =========================================================
# Backward-compatible generation function
# =========================================================

def generate_answer(
    question,
    context,
):
    """
    Backward-compatible LLM generation function.

    Existing callers receive only the answer string.
    """

    result = generate_answer_with_metadata(
        question,
        context,
    )

    return result["answer"]
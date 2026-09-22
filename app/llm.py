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
    Raised when the Groq LLM cannot generate an answer.
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
# Usage extraction helper
# =========================================================

def _extract_usage(usage):
    """
    Extract token usage from different usage object formats.

    Supports:

    1. OpenAI/Groq usage objects with model_dump()
    2. Dictionary-based usage
    3. Simple mock/test objects with attributes
    """

    prompt_tokens = 0
    completion_tokens = 0
    total_tokens = 0
    reasoning_tokens = 0

    if not usage:
        return {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "reasoning_tokens": 0,
            "total_tokens": 0,
        }

    # -----------------------------------------------------
    # Convert usage into a dictionary when possible
    # -----------------------------------------------------

    if hasattr(usage, "model_dump"):
        usage_data = usage.model_dump()

    elif hasattr(usage, "to_dict"):
        usage_data = usage.to_dict()

    elif isinstance(usage, dict):
        usage_data = usage

    else:
        usage_data = {
            "prompt_tokens": getattr(
                usage,
                "prompt_tokens",
                0,
            ),
            "completion_tokens": getattr(
                usage,
                "completion_tokens",
                0,
            ),
            "total_tokens": getattr(
                usage,
                "total_tokens",
                0,
            ),
            "completion_tokens_details": getattr(
                usage,
                "completion_tokens_details",
                None,
            ),
        }

    # -----------------------------------------------------
    # Basic token counts
    # -----------------------------------------------------

    prompt_tokens = (
        usage_data.get(
            "prompt_tokens",
            0,
        )
        or 0
    )

    completion_tokens = (
        usage_data.get(
            "completion_tokens",
            0,
        )
        or 0
    )

    total_tokens = (
        usage_data.get(
            "total_tokens",
            0,
        )
        or 0
    )

    # -----------------------------------------------------
    # Reasoning tokens
    # -----------------------------------------------------

    completion_details = (
        usage_data.get(
            "completion_tokens_details"
        )
        or {}
    )

    if hasattr(
        completion_details,
        "model_dump",
    ):
        completion_details = (
            completion_details.model_dump()
        )

    elif hasattr(
        completion_details,
        "to_dict",
    ):
        completion_details = (
            completion_details.to_dict()
        )

    elif not isinstance(
        completion_details,
        dict,
    ):
        completion_details = {
            "reasoning_tokens": getattr(
                completion_details,
                "reasoning_tokens",
                0,
            )
        }

    reasoning_tokens = (
        completion_details.get(
            "reasoning_tokens",
            0,
        )
        or 0
    )

    return {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "reasoning_tokens": reasoning_tokens,
        "total_tokens": total_tokens,
    }


# =========================================================
# LLM generation with metadata
# =========================================================

def generate_answer_with_metadata(
    question,
    context,
):
    """
    Generate an answer using the Groq LLM.

    Returns both the answer and per-request monitoring
    metadata.

    Metadata includes:

    - model
    - latency
    - prompt tokens
    - completion tokens
    - reasoning tokens
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

    # -----------------------------------------------------
    # Configuration validation
    # -----------------------------------------------------

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
        # -------------------------------------------------
        # Call Groq
        # -------------------------------------------------

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

        # -------------------------------------------------
        # Extract usage metadata
        # -------------------------------------------------

        usage = getattr(
            response,
            "usage",
            None,
        )

        usage_data = _extract_usage(
            usage
        )

        prompt_tokens = usage_data[
            "prompt_tokens"
        ]

        completion_tokens = usage_data[
            "completion_tokens"
        ]

        reasoning_tokens = usage_data[
            "reasoning_tokens"
        ]

        total_tokens = usage_data[
            "total_tokens"
        ]

        # -------------------------------------------------
        # Metrics
        # -------------------------------------------------

        metrics.observe_latency(
            latency_ms
        )

        metrics.observe_llm_latency(
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

        # -------------------------------------------------
        # Logging
        # -------------------------------------------------

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
                "reasoning_tokens": reasoning_tokens,
                "total_tokens": total_tokens,
                "cost_usd": round(
                    cost_usd,
                    8,
                ),
            },
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

        if not answer:
            metrics.increment(
                "llm_empty_response_total"
            )

            raise LLMServiceError(
                "The Groq LLM returned an empty response."
            )

        # -------------------------------------------------
        # Return answer + metadata
        # -------------------------------------------------

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
                "reasoning_tokens": reasoning_tokens,
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

        metrics.observe_llm_latency(
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
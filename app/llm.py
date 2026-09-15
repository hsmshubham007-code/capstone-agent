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

GROQ_API_KEY = os.getenv(
    "GROQ_API_KEY"
)

MODEL = os.getenv(
    "GROQ_MODEL"
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
# Groq client
# =========================================================

def get_client():
    if not GROQ_API_KEY:
        raise LLMServiceError(
            "GROQ_API_KEY is missing."
        )

    return OpenAI(
        api_key=GROQ_API_KEY,
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
# LLM generation
# =========================================================

def generate_answer(
    question,
    context,
):
    """
    Generate an answer using the Groq LLM.

    Monitoring records:
    - request count
    - latency
    - prompt tokens
    - completion tokens
    - total tokens
    - estimated cost
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

    if not GROQ_API_KEY:
        metrics.increment(
            "llm_configuration_errors_total"
        )

        logger.error(
            "GROQ_API_KEY is not configured"
        )

        raise LLMServiceError(
            "The Groq API key is not configured."
        )

    if not MODEL:
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
        # Create Groq client
        # -------------------------------------------------

        client = get_client()

        # -------------------------------------------------
        # Groq API call
        # -------------------------------------------------

        response = client.chat.completions.create(
            model=MODEL,
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
            time.perf_counter()
            - start_time
        ) * 1000

        metrics.observe_latency(
            latency_ms
        )

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

        metrics.record_llm_usage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
        )

        # -------------------------------------------------
        # Calculate estimated cost
        # -------------------------------------------------

        cost_usd = calculate_cost(
            model=MODEL,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
        )

        metrics.record_cost(
            cost_usd
        )

        # -------------------------------------------------
        # Success counter
        # -------------------------------------------------

        metrics.increment(
            "llm_requests_success_total"
        )

        # -------------------------------------------------
        # Log successful request
        # -------------------------------------------------

        logger.info(
            "LLM request completed",
            extra={
                "model": MODEL,
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

        return answer.strip()

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
                "model": MODEL,
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
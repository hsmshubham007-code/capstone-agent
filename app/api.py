import logging
import os
import time
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

from app.agent import run_agent
from app.llm import LLMServiceError
from app.logging_config import setup_logging
from app.metrics import metrics
from app.retrieval import get_embeddings

# =========================================================
# Logging
# =========================================================

setup_logging()

logger = logging.getLogger(
    "company-policy-agent.api"
)


# =========================================================
# FastAPI application
# =========================================================

app = FastAPI(
    title="Company Policy Agent API",
    description="Production Company Policy Agent using LangGraph + RAG",
    version="1.1.0",
)


# =========================================================
# Startup warm-up
# =========================================================

@app.on_event("startup")
def warmup_retrieval():
    """
    Load the embedding model during application startup.

    This prevents the first /chat request from paying the
    model initialization/download cost.
    """

    logger.info(
        "Starting retrieval warm-up"
    )

    start_time = time.perf_counter()

    try:
        get_embeddings()

        latency_ms = (
            time.perf_counter()
            - start_time
        ) * 1000

        logger.info(
            "Retrieval warm-up completed",
            extra={
                "latency_ms": round(
                    latency_ms,
                    2,
                ),
            },
        )

    except Exception as exc:
        logger.exception(
            "Retrieval warm-up failed",
            extra={
                "error": str(exc),
            },
        )

        raise


# =========================================================
# Request / Response models
# =========================================================

class ChatRequest(BaseModel):
    question: str
    thread_id: str | None = None


class ChatResponse(BaseModel):
    request_id: str
    thread_id: str
    answer: str
    sources: list[str]
    tools_used: list[str]
    trace: list[dict]


# =========================================================
# Request ID + Monitoring Middleware
# =========================================================

@app.middleware("http")
async def request_logging_middleware(
    request: Request,
    call_next,
):
    """
    Add a request ID to every HTTP request.

    Records:
    - total requests
    - successful requests
    - failed requests
    - request latency
    - structured logs
    """

    request_id = request.headers.get(
        "X-Request-ID"
    ) or str(uuid4())

    request.state.request_id = request_id

    start_time = time.perf_counter()

    metrics.increment(
        "requests_total"
    )

    try:

        response = await call_next(request)

        latency_ms = (
            time.perf_counter()
            - start_time
        ) * 1000

        metrics.observe_latency(
            latency_ms
        )

        if response.status_code < 400:

            metrics.increment(
                "requests_success_total"
            )

        else:

            metrics.increment(
                "requests_errors_total"
            )

        response.headers[
            "X-Request-ID"
        ] = request_id

        logger.info(
            "HTTP request completed",
            extra={
                "request_id": request_id,
                "endpoint": request.url.path,
                "method": request.method,
                "status": response.status_code,
                "latency_ms": round(
                    latency_ms,
                    2,
                ),
            },
        )

        return response

    except Exception as exc:

        latency_ms = (
            time.perf_counter()
            - start_time
        ) * 1000

        metrics.increment(
            "requests_errors_total"
        )

        metrics.observe_latency(
            latency_ms
        )

        logger.exception(
            "HTTP request failed",
            extra={
                "request_id": request_id,
                "endpoint": request.url.path,
                "method": request.method,
                "status": 500,
                "latency_ms": round(
                    latency_ms,
                    2,
                ),
                "error": str(exc),
            },
        )

        raise


# =========================================================
# Root endpoint
# =========================================================

@app.get("/")
def root():
    """
    Basic service information.
    """

    return {
        "service": "company-policy-agent",
        "version": "1.1.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
        "ready": "/ready",
        "metrics": "/metrics",
    }


# =========================================================
# Health check
# =========================================================

@app.get("/health")
def health():
    """
    Liveness check.

    Only verifies that the API process is alive.
    """

    return {
        "status": "healthy",
        "service": "company-policy-agent",
        "version": "1.1.0",
    }


# =========================================================
# Readiness check
# =========================================================

@app.get("/ready")
def ready():
    """
    Readiness check.

    Verifies required configuration
    and persistent storage.
    """

    groq_api_key = os.getenv(
        "GROQ_API_KEY"
    )

    groq_model = os.getenv(
        "GROQ_MODEL"
    )

    chroma_path = os.getenv(
        "CHROMA_PATH",
        "storage/chroma",
    )

    checkpoint_path = os.getenv(
        "CHECKPOINT_DIR",
        "storage/checkpoints",
    )

    checks = {
        "groq_api_key": bool(
            groq_api_key
        ),
        "groq_model": bool(
            groq_model
        ),
        "chroma_storage": os.path.isdir(
            chroma_path
        ),
        "checkpoint_storage": os.path.isdir(
            checkpoint_path
        ),
    }

    ready_status = all(
        checks.values()
    )

    if not ready_status:

        logger.warning(
            "Application is not ready",
            extra={
                "status": "not_ready",
            },
        )

        raise HTTPException(
            status_code=503,
            detail={
                "status": "not_ready",
                "checks": checks,
            },
        )

    return {
        "status": "ready",
        "service": "company-policy-agent",
        "checks": checks,
    }


# =========================================================
# Metrics
# =========================================================

@app.get("/metrics")
def get_metrics():
    """
    Return application monitoring metrics.

    Includes:
    - request count
    - success/error count
    - average latency
    - p50 latency
    - p95 latency
    - chat latency
    - retrieval latency
    - LLM latency
    - LLM token usage
    - LLM errors
    - cost information
    """

    return metrics.snapshot()


# =========================================================
# Chat
# =========================================================

@app.post(
    "/chat",
    response_model=ChatResponse,
)
def chat(
    request: ChatRequest,
    http_request: Request,
):
    """
    Execute the Company Policy Agent.

    All chat requests go through run_agent(), which
    performs input validation and prompt-injection
    detection before invoking the LangGraph workflow.
    """

    request_id = getattr(
        http_request.state,
        "request_id",
        str(uuid4()),
    )

    thread_id = (
        request.thread_id
        or str(uuid4())
    )

    logger.info(
        "Chat request started",
        extra={
            "request_id": request_id,
            "thread_id": thread_id,
            "endpoint": "/chat",
        },
    )

    start_time = time.perf_counter()

    try:

        result = run_agent(
            question=request.question,
            session_id=thread_id,
            request_id=request_id,
        )

    except LLMServiceError as exc:

        latency_ms = (
            time.perf_counter()
            - start_time
        ) * 1000

        metrics.observe_chat_latency(
            latency_ms
        )

        metrics.increment(
            "llm_service_errors_total"
        )

        logger.error(
            "LLM service unavailable",
            extra={
                "request_id": request_id,
                "thread_id": thread_id,
                "endpoint": "/chat",
                "status": 503,
                "latency_ms": round(
                    latency_ms,
                    2,
                ),
                "error": str(exc),
            },
        )

        raise HTTPException(
            status_code=503,
            detail={
                "error": "llm_unavailable",
                "message": str(exc),
                "request_id": request_id,
                "thread_id": thread_id,
            },
        ) from exc

    except (
        TypeError,
        ValueError,
    ) as exc:

        latency_ms = (
            time.perf_counter()
            - start_time
        ) * 1000

        metrics.observe_chat_latency(
            latency_ms
        )

        logger.warning(
            "Invalid chat request",
            extra={
                "request_id": request_id,
                "thread_id": thread_id,
                "endpoint": "/chat",
                "status": 400,
                "latency_ms": round(
                    latency_ms,
                    2,
                ),
                "error": str(exc),
            },
        )

        raise HTTPException(
            status_code=400,
            detail={
                "error": "invalid_request",
                "message": str(exc),
                "request_id": request_id,
                "thread_id": thread_id,
            },
        ) from exc

    except Exception as exc:

        latency_ms = (
            time.perf_counter()
            - start_time
        ) * 1000

        metrics.observe_chat_latency(
            latency_ms
        )

        metrics.increment(
            "agent_errors_total"
        )

        logger.exception(
            "Agent request failed",
            extra={
                "request_id": request_id,
                "thread_id": thread_id,
                "endpoint": "/chat",
                "status": 500,
                "latency_ms": round(
                    latency_ms,
                    2,
                ),
                "error": str(exc),
            },
        )

        raise HTTPException(
            status_code=500,
            detail={
                "error": "agent_error",
                "message": (
                    "The agent could not "
                    "complete the request."
                ),
                "request_id": request_id,
                "thread_id": thread_id,
            },
        ) from exc

    # -----------------------------------------------------
    # Successful chat latency
    # -----------------------------------------------------

    latency_ms = (
        time.perf_counter()
        - start_time
    ) * 1000

    metrics.observe_chat_latency(
        latency_ms
    )

    metrics.increment(
        "chat_requests_success_total"
    )

    if result.get("tools_used"):
        metrics.increment(
            "tool_using_requests_total"
        )

    if result.get("sources"):
        metrics.increment(
            "retrieval_success_total"
        )

    logger.info(
        "Chat request completed",
        extra={
            "request_id": request_id,
            "thread_id": thread_id,
            "endpoint": "/chat",
            "status": 200,
            "latency_ms": round(
                latency_ms,
                2,
            ),
            "tool": result.get(
                "tool",
                "",
            ),
            "tools_used": result.get(
                "tools_used",
                [],
            ),
            "sources_count": len(
                result.get(
                    "sources",
                    [],
                )
            ),
        },
    )

    return {
        "request_id": request_id,
        "thread_id": thread_id,
        "answer": result.get(
            "answer",
            "",
        ),
        "sources": result.get(
            "sources",
            [],
        ),
        "tools_used": result.get(
            "tools_used",
            [],
        ),
        "trace": result.get(
            "trace",
            [],
        ),
    }


# =========================================================
# Checkpoint
# =========================================================

@app.get(
    "/checkpoint/{thread_id}"
)
def get_checkpoint(
    thread_id: str,
):
    """
    Retrieve the latest LangGraph checkpoint
    for a conversation thread.
    """

    try:

        from app.graph import graph

        state = graph.get_state(
            {
                "configurable": {
                    "thread_id": thread_id,
                }
            }
        )

    except Exception as exc:

        logger.exception(
            "Checkpoint lookup failed",
            extra={
                "thread_id": thread_id,
                "endpoint": (
                    "/checkpoint/"
                    + thread_id
                ),
                "status": 500,
                "error": str(exc),
            },
        )

        raise HTTPException(
            status_code=500,
            detail={
                "error": "checkpoint_error",
                "message": (
                    "Could not retrieve "
                    "the checkpoint."
                ),
                "thread_id": thread_id,
            },
        ) from exc

    if state is None:

        raise HTTPException(
            status_code=404,
            detail={
                "error": "checkpoint_not_found",
                "thread_id": thread_id,
            },
        )

    return {
        "checkpoint_id": state.config.get(
            "configurable",
            {},
        ).get(
            "checkpoint_id"
        ),
        "values": state.values,
    }
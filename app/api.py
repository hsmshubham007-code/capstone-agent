from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.graph import graph
from app.llm import LLMServiceError


app = FastAPI(
    title="Company Policy Agent API",
    description="LangGraph + RAG company policy agent",
    version="1.0.0"
)


class ChatRequest(BaseModel):
    question: str
    thread_id: str | None = None


class ChatResponse(BaseModel):
    thread_id: str
    answer: str
    sources: list[str]
    tools_used: list[str]
    trace: list[dict]


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "company-policy-agent"
    }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    thread_id = request.thread_id or str(uuid4())

    initial_state = {
        "session_id": thread_id,
        "question": request.question,
        "conversation_history": [],
        "tool": "",
        "answer": "",
        "sources": [],
        "tools_used": [],
        "trace": []
    }

    try:

        result = graph.invoke(
            initial_state,
            config={
                "configurable": {
                    "thread_id": thread_id
                }
            }
        )

    except LLMServiceError as exc:

        raise HTTPException(
            status_code=503,
            detail={
                "error": "llm_unavailable",
                "message": str(exc),
                "thread_id": thread_id,
                "failover": "Retry the request when the Groq service is available."
            }
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail={
                "error": "agent_error",
                "message": "The agent could not complete the request.",
                "thread_id": thread_id
            }
        ) from exc

    return {
        "thread_id": thread_id,
        "answer": result["answer"],
        "sources": result["sources"],
        "tools_used": result["tools_used"],
        "trace": result["trace"]
    }


@app.get("/checkpoint/{thread_id}")
def get_checkpoint(thread_id: str):

    state = graph.get_state(
        {
            "configurable": {
                "thread_id": thread_id
            }
        }
    )

    return {
        "thread_id": thread_id,
        "checkpoint_id": state.config.get(
            "configurable",
            {}
        ).get("checkpoint_id"),
        "values": state.values
    }
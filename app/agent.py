from app.audit import (
    create_request_id,
    record_tool_call,
)
from app.graph import graph
from app.guardrails import (
    detect_prompt_injection,
    validate_input,
    validate_output,
)
from app.memory import (
    add_message,
    get_history,
)


def run_agent(
    question,
    session_id="default",
):
    """
    Run the company policy agent.

    Every request receives a unique request_id.

    Safe tools can execute immediately.

    Risky tools are stopped and placed into
    the human approval queue.
    """

    request_id = create_request_id()

    question = validate_input(
        question
    )

    # -------------------------------------------------
    # Prompt injection guardrail
    # -------------------------------------------------

    if detect_prompt_injection(
        question
    ):
        record_tool_call(
            request_id=request_id,
            tool_name="guardrail",
            arguments={
                "question": question,
            },
            status="BLOCKED",
            outcome={
                "reason": "prompt_injection",
            },
        )

        return {
            "request_id": request_id,
            "question": question,
            "tool": "guardrail",
            "answer": (
                "I can't process requests that "
                "attempt to override the agent's "
                "instructions."
            ),
            "sources": [],
            "tools_used": [],
            "retrieval_metadata": {},
            "approval_id": "",
            "approval_status": "",
            "llm_metadata": None,
            "conversation_history": get_history(
                session_id
            ),
            "trace": [
                {
                    "step": "guardrail",
                    "tool": "guardrail",
                    "duration": 0,
                }
            ],
        }

    # -------------------------------------------------
    # Conversation history
    # -------------------------------------------------

    history = get_history(
        session_id
    )

    # -------------------------------------------------
    # Initial LangGraph state
    # -------------------------------------------------

    state = {
        "request_id": request_id,
        "session_id": session_id,
        "question": question,
        "conversation_history": history,
        "tool": "",
        "answer": "",
        "sources": [],
        "tools_used": [],
        "retrieval_metadata": {},
        "approval_id": "",
        "approval_status": "",
        "llm_metadata": None,
        "trace": [],
    }

    # -------------------------------------------------
    # Run graph
    # -------------------------------------------------

    result = graph.invoke(
        state,
        config={
            "configurable": {
                "thread_id": session_id,
            }
        },
    )

    # -------------------------------------------------
    # Validate final answer
    # -------------------------------------------------

    result["answer"] = validate_output(
        result["answer"]
    )

    # -------------------------------------------------
    # Store conversation
    # -------------------------------------------------

    add_message(
        session_id,
        "user",
        question,
    )

    add_message(
        session_id,
        "assistant",
        result["answer"],
    )

    result["conversation_history"] = (
        get_history(
            session_id
        )
    )

    # -------------------------------------------------
    # Preserve request ID
    # -------------------------------------------------

    result["request_id"] = request_id

    # -------------------------------------------------
    # Approval status
    # -------------------------------------------------

    if result.get(
        "approval_id"
    ):
        result["approval_status"] = (
            "PENDING"
        )
    else:
        result["approval_status"] = ""

    return result
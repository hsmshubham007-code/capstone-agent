from typing import Any, TypedDict


class AgentState(TypedDict):
    request_id: str

    session_id: str

    question: str

    conversation_history: list

    tool: str

    answer: str

    sources: list

    tools_used: list

    approval_id: str

    approval_status: str

    llm_metadata: dict[str, Any] | None

    trace: list
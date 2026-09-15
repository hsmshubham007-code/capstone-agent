from typing import TypedDict


class AgentState(TypedDict):

    request_id: str

    session_id: str

    question: str

    conversation_history: list[dict[str, str]]

    tool: str

    answer: str

    sources: list[str]

    tools_used: list[str]

    approval_id: str

    approval_status: str

    trace: list[dict]
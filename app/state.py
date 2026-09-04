from typing import TypedDict


class AgentState(TypedDict):
    session_id: str
    question: str
    conversation_history: list[dict[str, str]]
    tool: str
    answer: str
    sources: list[str]
    tools_used: list[str]
    trace: list[dict]
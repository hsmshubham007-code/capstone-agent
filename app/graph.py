import time
from typing import Literal

from langgraph.graph import END, START, StateGraph

from app.approval import create_approval_request
from app.audit import record_tool_call
from app.checkpoint import checkpointer
from app.router import decide_tool
from app.safety import requires_approval
from app.state import AgentState
from app.tools import search_documents_tool


def router_node(state: AgentState):

    start = time.perf_counter()

    tool = decide_tool(
        state["question"],
        state["conversation_history"],
    )

    duration = time.perf_counter() - start

    request_id = state.get("request_id")

    if request_id:
        record_tool_call(
            request_id=request_id,
            tool_name="router",
            arguments={
                "question": state["question"],
            },
            status="SUCCESS",
            outcome={
                "selected_tool": tool,
                "approval_required": requires_approval(tool),
            },
        )

    return {
        "tool": tool,
        "trace": state["trace"] + [
            {
                "step": "router",
                "tool": tool,
                "duration": duration,
            }
        ],
    }


def approval_node(state: AgentState):

    request_id = state["request_id"]
    tool_name = state["tool"]

    question = state["question"]

    # -------------------------------------------------
    # Build arguments for the risky tool
    # -------------------------------------------------

    if tool_name == "update_employee_record":

        import re

        employee_match = re.search(
            r"employee\s+(EMP\d+)",
            question,
            re.IGNORECASE,
        )

        salary_match = re.search(
            r"(?:salary\s+(?:to|of)\s+|\$)(\d+)",
            question,
            re.IGNORECASE,
        )

        if not employee_match:
            raise ValueError(
                "Could not identify employee ID."
            )

        if not salary_match:
            raise ValueError(
                "Could not identify new salary."
            )

        arguments = {
            "employee_id": employee_match.group(1),
            "field": "salary",
            "new_value": int(
                salary_match.group(1)
            ),
        }

    else:

        arguments = {
            "question": question,
        }

    # -------------------------------------------------
    # Create approval request
    # -------------------------------------------------

    approval = create_approval_request(
        request_id=request_id,
        tool_name=tool_name,
        arguments=arguments,
    )

    # -------------------------------------------------
    # Audit blocked tool
    # -------------------------------------------------

    record_tool_call(
        request_id=request_id,
        tool_name=tool_name,
        arguments=arguments,
        status="BLOCKED",
        outcome={
            "reason": "human_approval_required",
            "approval_id": approval["approval_id"],
        },
    )

    return {
        "answer": (
            "This action requires human approval "
            "before it can be executed."
        ),
        "approval_id": approval["approval_id"],
        "approval_status": "PENDING",
        "sources": [],
        "tools_used": [],
        "trace": state["trace"] + [
            {
                "step": "approval_required",
                "tool": tool_name,
                "approval_id": approval["approval_id"],
                "status": "PENDING",
                "duration": 0,
            }
        ],
    }



def search_node(state: AgentState):

    start = time.perf_counter()

    result = search_documents_tool(
        question=state["question"],
        history=state["conversation_history"],
        request_id=state.get("request_id"),
    )

    duration = time.perf_counter() - start

    return {
        "answer": result["answer"],
        "sources": result["sources"],
        "tools_used": [result["name"]],
        "trace": state["trace"] + [
            {
                "step": "search_documents",
                "tool": result["name"],
                "sources": result["sources"],
                "results": result["results"],
                "duration": duration,
            }
        ],
    }


def no_tool_node(state: AgentState):

    return {
        "answer": "I don't have a tool that can answer this question.",
        "sources": [],
        "tools_used": [],
        "trace": state["trace"] + [
            {
                "step": "no_tool",
                "tool": "no_tool",
                "duration": 0,
            }
        ],
    }


def route_after_router(
    state: AgentState,
) -> Literal[
    "search",
    "approval",
    "no_tool",
]:

    tool = state["tool"]

    if tool == "search_documents":
        return "search"

    if requires_approval(tool):
        return "approval"

    return "no_tool"


builder = StateGraph(AgentState)


builder.add_node(
    "router",
    router_node,
)

builder.add_node(
    "search",
    search_node,
)

builder.add_node(
    "approval",
    approval_node,
)

builder.add_node(
    "no_tool",
    no_tool_node,
)


builder.add_edge(
    START,
    "router",
)


builder.add_conditional_edges(
    "router",
    route_after_router,
    {
        "search": "search",
        "approval": "approval",
        "no_tool": "no_tool",
    },
)


builder.add_edge(
    "search",
    END,
)

builder.add_edge(
    "approval",
    END,
)

builder.add_edge(
    "no_tool",
    END,
)


graph = builder.compile(
    checkpointer=checkpointer,
)
import re
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


def _extract_employee_id(question: str) -> str | None:
    """Extract and normalize an employee ID from the request."""

    patterns = [
        (
            r"\bemployee\s+(?:record\s+)?(?:ID\s*)?[:#]?\s*"
            r"(EMP-?\d+|\d+)\b"
        ),
        r"\b(EMP-?\d+)\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, question, re.IGNORECASE)

        if match:
            employee_id = match.group(1).upper()

            if employee_id.startswith("EMP"):
                digits = re.sub(r"\D", "", employee_id)
                return f"EMP{digits}"

            return f"EMP{employee_id}"

    return None


def _extract_salary(question: str) -> int | None:
    """Extract a positive integer salary from the request."""

    patterns = [
        # Examples:
        # salary to ₹80,000
        # salary of Rs. 80,000
        # salary to INR 80000
        # salary to 80,000 per month
        (
            r"\bsalary\b[^\d]{0,40}"
            r"([\d][\d,]*(?:\.\d{1,2})?)"
        ),

        # Examples:
        # change salary to ₹80,000
        # update salary to Rs. 80,000
        (
            r"\b(?:to|at)\s*[^\d]{0,20}"
            r"([\d][\d,]*(?:\.\d{1,2})?)"
        ),
    ]

    for pattern in patterns:
        match = re.search(pattern, question, re.IGNORECASE)

        if not match:
            continue

        raw_amount = match.group(1).replace(",", "")

        try:
            amount = float(raw_amount)
        except ValueError:
            continue

        if amount > 0 and amount.is_integer():
            return int(amount)

    return None


def router_node(state: AgentState) -> dict:
    """Choose the appropriate tool for the request."""

    start_time = time.perf_counter()

    question = state["question"]
    history = state.get("conversation_history", [])

    tool_name = decide_tool(question, history)

    duration_ms = round(
        (time.perf_counter() - start_time) * 1000,
        2,
    )

    request_id = state.get("request_id", "")

    if request_id:
        record_tool_call(
            request_id=request_id,
            tool_name="router",
            arguments={"question": question},
            status="SUCCESS",
            outcome={"selected_tool": tool_name},
        )

    trace_entry = {
        "step": "router",
        "duration": duration_ms,
    }

    return {
        "tool": tool_name,
        "trace": state.get("trace", []) + [trace_entry],
    }


def route_after_router(
    state: AgentState,
) -> Literal["approval", "search", "no_tool"]:
    """Route risky actions through the approval node."""

    tool_name = state.get("tool")

    if tool_name and requires_approval(tool_name):
        return "approval"

    if tool_name == "search_documents":
        return "search"

    return "no_tool"


def approval_node(state: AgentState) -> dict:
    """Create a pending approval request without executing it."""

    start_time = time.perf_counter()

    question = state["question"]
    tool_name = state.get("tool")
    request_id = state.get("request_id", "")

    if not tool_name:
        raise ValueError("Could not identify the requested tool.")

    # Extract arguments for the supported risky tools.
    if tool_name == "update_employee_record":
        employee_id = _extract_employee_id(question)

        if not employee_id:
            raise ValueError("Could not identify employee ID.")

        new_salary = _extract_salary(question)

        if new_salary is None:
            raise ValueError("Could not identify new salary.")

        arguments = {
            "employee_id": employee_id,
            "field": "salary",
            "new_value": new_salary,
        }

    elif tool_name == "delete_employee_record":
        employee_id = _extract_employee_id(question)

        if not employee_id:
            raise ValueError("Could not identify employee ID.")

        arguments = {
            "employee_id": employee_id,
        }

    else:
        raise ValueError(
            f"Approval argument extraction is not implemented "
            f"for tool: {tool_name}"
        )

    approval = create_approval_request(
        request_id=request_id,
        tool_name=tool_name,
        arguments=arguments,
    )

    approval_id = approval["approval_id"]
    approval_status = approval["status"]

    record_tool_call(
        request_id=request_id,
        tool_name=tool_name,
        arguments=arguments,
        status="BLOCKED",
        outcome={
            "approval_id": approval_id,
            "approval_status": approval_status,
        },
    )

    answer = (
        f"Human approval is required before executing "
        f"{tool_name}. "
        f"Approval request ID: {approval_id}. "
        f"Status: {approval_status}. "
        "No changes have been made."
    )

    duration_ms = round(
        (time.perf_counter() - start_time) * 1000,
        2,
    )

    trace_entry = {
        "step": "approval",
        "duration": duration_ms,
        "approval_id": approval_id,
        "approval_status": approval_status,
        "arguments": arguments,
    }

    return {
        "answer": answer,
        "approval_id": approval_id,
        "approval_status": approval_status,
        "sources": [],
        "tools_used": state.get("tools_used", []) + [tool_name],
        "trace": state.get("trace", []) + [trace_entry],
    }


def search_node(state: AgentState) -> dict:
    """Search company policy documents using the existing tool."""

    start_time = time.perf_counter()

    question = state["question"]
    history = state.get("conversation_history", [])
    request_id = state.get("request_id")

    result = search_documents_tool(
        question=question,
        history=history,
        request_id=request_id,
    )

    elapsed_ms = round(
        (time.perf_counter() - start_time) * 1000,
        2,
    )

    sources = result.get("sources", [])
    retrieved_results = result.get("results", [])

    trace_entry = {
        "step": "search_documents",
        "duration": elapsed_ms,
        "results": retrieved_results,
    }

    return {
        "answer": result["answer"],
        "sources": sources,
        "tools_used": state.get("tools_used", []) + ["search_documents"],
        "retrieval_metadata": result.get("retrieval_metadata"),
        "llm_metadata": result.get("llm_metadata"),
        "trace": state.get("trace", []) + [trace_entry],
    }


def no_tool_node(state: AgentState) -> dict:
    """Respond when no suitable tool is selected."""

    start_time = time.perf_counter()

    answer = (
        "I don't have enough information to answer this request "
        "using the available company-policy tools. "
        "Please clarify what you would like to know."
    )

    duration_ms = round(
        (time.perf_counter() - start_time) * 1000,
        2,
    )

    trace_entry = {
        "step": "no_tool",
        "duration": duration_ms,
    }

    return {
        "answer": answer,
        "sources": [],
        "tools_used": state.get("tools_used", []),
        "trace": state.get("trace", []) + [trace_entry],
    }


def build_graph():
    """Build and compile the Company Policy Agent graph."""

    workflow = StateGraph(AgentState)

    workflow.add_node("router", router_node)
    workflow.add_node("approval", approval_node)
    workflow.add_node("search", search_node)
    workflow.add_node("no_tool", no_tool_node)

    workflow.add_edge(START, "router")

    workflow.add_conditional_edges(
        "router",
        route_after_router,
        {
            "approval": "approval",
            "search": "search",
            "no_tool": "no_tool",
        },
    )

    workflow.add_edge("approval", END)
    workflow.add_edge("search", END)
    workflow.add_edge("no_tool", END)

    return workflow.compile(checkpointer=checkpointer)


graph = build_graph()
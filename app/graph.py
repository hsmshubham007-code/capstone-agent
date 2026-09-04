import time

from typing import Literal

from langgraph.graph import END, START, StateGraph

from app.router import decide_tool
from app.state import AgentState
from app.tools import search_documents_tool


def router_node(state: AgentState):
    start = time.perf_counter()

    tool = decide_tool(
        state["question"],
        state["conversation_history"]
    )

    duration = time.perf_counter() - start

    return {
        "tool": tool,
        "trace": state["trace"] + [
            {
                "step": "router",
                "tool": tool,
                "duration": duration
            }
        ]
    }


def search_node(state: AgentState):
    start = time.perf_counter()

    result = search_documents_tool(
        state["question"],
        state["conversation_history"]
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
               "duration": duration
            }
        ]
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
                "duration": 0
            }
        ]
    }

def route_after_router(
    state: AgentState
) -> Literal["search", "no_tool"]:

    if state["tool"] == "search_documents":
        return "search"

    return "no_tool"


builder = StateGraph(AgentState)

builder.add_node("router", router_node)
builder.add_node("search", search_node)
builder.add_node("no_tool", no_tool_node)

builder.add_edge(START, "router")

builder.add_conditional_edges(
    "router",
    route_after_router,
    {
        "search": "search",
        "no_tool": "no_tool"
    }
)

builder.add_edge("search", END)
builder.add_edge("no_tool", END)

graph = builder.compile()
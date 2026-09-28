import asyncio
import uuid

import requests
import streamlit as st

from app.async_tools import (
    run_tools_parallel,
    run_tools_sequential,
)

st.set_page_config(
    page_title="Company Policy Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# CONFIGURATION
# ============================================================

# Production FastAPI endpoint.
# Docker Compose maps:
# host port 8000 -> container port 8000
API_URL = "http://localhost:8000"


# ============================================================
# PAGE HEADER
# ============================================================

st.title("🤖 Company Policy Agent")

st.caption(
    "Company policy assistant with RAG, LangGraph, "
    "checkpointing, and human approval"
)


# ============================================================
# SESSION / THREAD
# ============================================================

if "session_id" not in st.session_state:
    st.session_state.session_id = str(
        uuid.uuid4()
    )


thread_id = st.session_state.session_id


if "messages" not in st.session_state:
    st.session_state.messages = []


# ============================================================
# SIDEBAR - CHECKPOINTING
# ============================================================

with st.sidebar:

    st.header("Checkpointing")

    st.caption(
        "LangGraph durable conversation state"
    )

    st.write(
        "**Thread ID**"
    )

    st.code(
        thread_id,
        language="text",
    )

    st.divider()

    try:

        checkpoint_response = requests.get(
            f"{API_URL}/checkpoint/{thread_id}",
            timeout=5,
        )

        if checkpoint_response.ok:

            checkpoint_data = (
                checkpoint_response.json()
            )

            st.success(
                "Checkpoint available"
            )

            values = checkpoint_data.get(
                "values",
                {},
            )

            if values:

                st.write(
                    "**Conversation state**"
                )

                approval_status = values.get(
                    "approval_status",
                    "",
                )

                if approval_status:

                    st.write(
                        f"Approval: "
                        f"`{approval_status}`"
                    )

                question = values.get(
                    "question",
                    "",
                )

                if question:

                    st.write(
                        f"Last question: "
                        f"`{question}`"
                    )

        else:

            st.info(
                "No checkpoint state available yet."
            )

    except requests.RequestException:

        st.info(
            "Checkpoint information unavailable."
        )


# ============================================================
# API HELPERS
# ============================================================

def call_chat_api(
    question,
    thread_id,
):
    """
    Send the production chat request to FastAPI.

    FastAPI owns:
    - LangGraph execution
    - RAG
    - LLM calls
    - checkpointing
    - metrics
    - audit logging
    - approval state
    """

    try:

        response = requests.post(
            f"{API_URL}/chat",
            json={
                "question": question,
                "thread_id": thread_id,
            },
            timeout=120,
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as exc:

        st.error(
            f"Chat API request failed: {exc}"
        )

        return None


def get_approval_from_api(
    approval_id,
):
    """
    Retrieve the authoritative approval state
    from the FastAPI backend.
    """

    try:

        response = requests.get(
            f"{API_URL}/approvals/{approval_id}",
            timeout=10,
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as exc:

        st.error(
            f"Could not retrieve approval request: "
            f"{exc}"
        )

        return None


def approve_via_api(
    approval_id,
):
    """
    Approve the request through FastAPI.
    """

    try:

        response = requests.post(
            f"{API_URL}/approvals/{approval_id}/approve",
            timeout=10,
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as exc:

        st.error(
            f"Approval failed: {exc}"
        )

        return None


def reject_via_api(
    approval_id,
):
    """
    Reject the request through FastAPI.
    """

    try:

        response = requests.post(
            f"{API_URL}/approvals/{approval_id}/reject",
            timeout=10,
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as exc:

        st.error(
            f"Rejection failed: {exc}"
        )

        return None


def execute_via_api(
    approval_id,
):
    """
    Execute an approved request through FastAPI.
    """

    try:

        response = requests.post(
            f"{API_URL}/approvals/{approval_id}/execute",
            timeout=30,
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as exc:

        st.error(
            f"Execution failed: {exc}"
        )

        return None


# ============================================================
# DISPLAY HELPERS
# ============================================================

def display_sources(
    sources,
):
    """Display retrieved document sources."""

    if not sources:
        return

    for source in sources:

        if isinstance(
            source,
            dict,
        ):

            source_name = (
                source.get("source")
                or source.get("file")
                or source.get("document")
                or "Unknown source"
            )

            page = source.get(
                "page"
            )

            if page is not None:

                st.markdown(
                    f"- **{source_name}** "
                    f"(page {page})"
                )

            else:

                st.markdown(
                    f"- **{source_name}**"
                )

        else:

            st.markdown(
                f"- **{source}**"
            )


def display_tools(
    tools,
):
    """Display tools used by the agent."""

    if isinstance(
        tools,
        dict,
    ):

        tools = list(
            tools.keys()
        )

    if isinstance(
        tools,
        list,
    ):

        for tool in tools:

            st.markdown(
                f"- `{tool}`"
            )

    else:

        st.markdown(
            f"- `{tools}`"
        )


# ============================================================
# HUMAN APPROVAL
# ============================================================

def display_approval(
    approval_id,
):
    """
    Display a clean HITL approval card.

    Only two actions are exposed:
    - Approve
    - Reject

    Approve automatically performs:
    PENDING -> APPROVED -> EXECUTED
    """

    if not approval_id:
        return

    approval = get_approval_from_api(
        approval_id
    )

    if not approval:
        return

    status = approval.get(
        "status",
        "UNKNOWN",
    )

    tool_name = approval.get(
        "tool_name",
        "Unknown tool",
    )

    arguments = approval.get(
        "arguments",
        {},
    )

    # --------------------------------------------------------
    # PENDING
    # --------------------------------------------------------

    if status == "PENDING":

        st.warning(
            "### Human approval required"
        )

        st.write(
            f"**Action:** `{tool_name}`"
        )

        st.write(
            "**Arguments:**"
        )

        st.json(
            arguments
        )

        st.caption(
            f"Approval ID: {approval_id}"
        )

        col1, col2 = st.columns(
            2
        )

        with col1:

            if st.button(
                "✅ Approve",
                key=f"approve_{approval_id}",
                use_container_width=True,
            ):

                approved = approve_via_api(
                    approval_id
                )

                if approved:

                    execution = execute_via_api(
                        approval_id
                    )

                    if execution:

                        st.success(
                            "Action approved and executed."
                        )

                        st.rerun()

        with col2:

            if st.button(
                "❌ Reject",
                key=f"reject_{approval_id}",
                use_container_width=True,
            ):

                rejected = reject_via_api(
                    approval_id
                )

                if rejected:

                    st.error(
                        "Action rejected. "
                        "No changes were made."
                    )

                    st.rerun()

    # --------------------------------------------------------
    # EXECUTED
    # --------------------------------------------------------

    elif status == "EXECUTED":

        st.success(
            "✅ Action approved and executed."
        )

        result = approval.get(
            "result"
        )

        if result:

            st.write(
                "**Result:**"
            )

            st.json(
                result
            )

    # --------------------------------------------------------
    # REJECTED
    # --------------------------------------------------------

    elif status == "REJECTED":

        st.error(
            "❌ Action rejected. "
            "No changes were made."
        )

    # --------------------------------------------------------
    # APPROVED
    # --------------------------------------------------------

    elif status == "APPROVED":

        st.info(
            "Action approved. "
            "Execution is in progress."
        )

    # --------------------------------------------------------
    # UNKNOWN
    # --------------------------------------------------------

    else:

        st.info(
            f"Approval status: `{status}`"
        )


# ============================================================
# CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    if message["role"] == "user":

        with st.chat_message("user"):

            st.markdown(
                message["content"]
            )

    elif message["role"] == "assistant":

        with st.chat_message("assistant"):

            st.markdown(
                message["content"]
            )

            result = message.get(
                "result",
                {},
            )

            # ------------------------------------------------
            # APPROVAL
            # ------------------------------------------------

            approval_id = result.get(
                "approval_id",
                "",
            )

            if approval_id:

                display_approval(
                    approval_id
                )

            # ------------------------------------------------
            # TOOLS
            # ------------------------------------------------

            tools = result.get(
                "tools",
                [],
            )

            if tools:

                with st.expander(
                    "🔧 Tools Used"
                ):

                    display_tools(
                        tools
                    )

            # ------------------------------------------------
            # SOURCES
            # ------------------------------------------------

            sources = result.get(
                "sources",
                [],
            )

            if sources:

                with st.expander(
                    "📚 Sources Cited"
                ):

                    display_sources(
                        sources
                    )


# ============================================================
# CHAT INPUT
# ============================================================

question = st.chat_input(
    "Ask a company policy question..."
)


if question:

    # --------------------------------------------------------
    # DISPLAY USER MESSAGE
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    with st.chat_message("user"):

        st.markdown(
            question
        )

    # --------------------------------------------------------
    # RUN AGENT
    # --------------------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner(
            "Running agent..."
        ):

            # =================================================
            # ASYNC PERFORMANCE BENCHMARK
            # =================================================

            sequential_result = asyncio.run(
                run_tools_sequential(
                    question
                )
            )

            sequential_latency = (
                sequential_result["latency"]
            )

            parallel_result = asyncio.run(
                run_tools_parallel(
                    question
                )
            )

            parallel_latency = (
                parallel_result["latency"]
            )

            reduction = (
                sequential_latency
                - parallel_latency
            )

            if sequential_latency > 0:

                reduction_percent = (
                    reduction
                    / sequential_latency
                ) * 100

            else:

                reduction_percent = 0

            if parallel_latency > 0:

                speedup = (
                    sequential_latency
                    / parallel_latency
                )

            else:

                speedup = 0

            # =================================================
            # PRODUCTION AGENT
            # =================================================

            graph_result = call_chat_api(
                question,
                thread_id,
            )

            if graph_result is None:

                st.stop()

        # ----------------------------------------------------
        # AGENT ANSWER
        # ----------------------------------------------------

        st.markdown(
            graph_result.get(
                "answer",
                "",
            )
        )

        # ----------------------------------------------------
        # APPROVAL
        # ----------------------------------------------------

        approval_id = graph_result.get(
            "approval_id",
            "",
        )

        if approval_id:

            display_approval(
                approval_id
            )

        # ----------------------------------------------------
        # TOOLS
        # ----------------------------------------------------

        tools_used = graph_result.get(
            "tools_used",
            [],
        )

        if tools_used:

            with st.expander(
                "🔧 Tools Used"
            ):

                display_tools(
                    tools_used
                )

        # ----------------------------------------------------
        # SOURCES
        # ----------------------------------------------------

        sources = graph_result.get(
            "sources",
            [],
        )

        if sources:

            with st.expander(
                "📚 Sources Cited"
            ):

                display_sources(
                    sources
                )

        # ----------------------------------------------------
        # LATENCY
        # ----------------------------------------------------

        with st.expander(
            "⏱️ Detailed Latency"
        ):

            st.write(
                "Sequential retrieval: "
                f"**{sequential_latency:.3f} seconds**"
            )

            st.write(
                "Parallel retrieval: "
                f"**{parallel_latency:.3f} seconds**"
            )

            st.write(
                "Latency reduction: "
                f"**{reduction:.3f} seconds**"
            )

            st.write(
                "Latency reduction percentage: "
                f"**{reduction_percent:.2f}%**"
            )

            st.write(
                "Speedup: "
                f"**{speedup:.2f}x**"
            )

        # ----------------------------------------------------
        # SAVE MESSAGE
        # ----------------------------------------------------

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": graph_result.get(
                    "answer",
                    "",
                ),
                "result": {
                    "sequential_latency":
                        sequential_latency,

                    "parallel_latency":
                        parallel_latency,

                    "reduction":
                        reduction,

                    "reduction_percent":
                        reduction_percent,

                    "speedup":
                        speedup,

                    "total_latency":
                        parallel_latency,

                    "tools":
                        tools_used,

                    "sources":
                        sources,

                    "approval_id":
                        approval_id,

                    "approval_status":
                        graph_result.get(
                            "approval_status",
                            "",
                        ),
                },
            }
        )
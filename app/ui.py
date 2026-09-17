import asyncio
import uuid

import requests
import streamlit as st

from app.approval import (
    approve_request,
    execute_approved_request,
    get_approval_request,
)
from app.async_tools import (
    run_tools_parallel,
    run_tools_sequential,
)

st.set_page_config(
    page_title="Company Policy Agent",
    page_icon="🤖",
    layout="wide",
)


st.title("🤖 Company Policy Agent")

st.caption(
    "Async RAG agent with LangGraph durable checkpointing"
)


# ============================================================
# CONFIGURATION
# ============================================================

API_URL = "http://localhost:8000"


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
# API HELPER
# ============================================================

def call_chat_api(question, thread_id):
    """
    Send the production chat request to the FastAPI backend.

    The FastAPI service owns:
    - LangGraph execution
    - RAG
    - LLM calls
    - checkpointing
    - metrics
    - audit logging
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
            f"❌ Unable to connect to Company Policy Agent API: "
            f"{exc}"
        )

        return None


# ============================================================
# DISPLAY HELPERS
# ============================================================

def display_tools(tools):

    for tool_name, branches in tools.items():

        st.markdown(
            f"🔎 **`{tool_name}`**"
        )

        for branch in branches:

            st.markdown(
                f"&nbsp;&nbsp;&nbsp;&nbsp;└── `{branch}`"
            )


def display_sources(sources):

    if not sources:

        st.info(
            "No sources were retrieved."
        )

        return

    for source in sources:

        if isinstance(source, dict):

            source_name = source.get(
                "source",
                "Unknown source",
            )

            st.markdown(
                f"📄 **{source_name}**"
            )

            if "page" in source:

                st.write(
                    f"Page: `{source['page']}`"
                )

            if "tool" in source:

                st.write(
                    f"Retrieval branch: "
                    f"`{source['tool']}`"
                )

            if "score" in source:

                st.write(
                    f"Similarity score: "
                    f"`{source['score']:.4f}`"
                )

        elif isinstance(source, str):

            st.markdown(
                f"📄 **{source}**"
            )

            st.write(
                "Source retrieved from the company "
                "policy knowledge base."
            )

        else:

            st.markdown(
                f"📄 **{source!s}**"
            )

        st.divider()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("💾 Checkpoint")

    st.write(
        "This chat uses a persistent LangGraph thread "
        "managed by the FastAPI backend."
    )

    st.code(
        thread_id,
        language="text",
    )

    try:

        checkpoint_response = requests.get(
            f"{API_URL}/checkpoint/{thread_id}",
            timeout=5,
        )

        if checkpoint_response.status_code == 200:

            checkpoint_data = (
                checkpoint_response.json()
            )

            values = checkpoint_data.get(
                "values",
                {},
            )

            st.success(
                "Checkpoint found"
            )

            st.write(
                f"Tool: "
                f"`{values.get('tool', '')}`"
            )

            st.write(
                f"Sources: "
                f"{len(values.get('sources', []))}"
            )

            st.write(
                f"Trace steps: "
                f"{len(values.get('trace', []))}"
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

        else:

            st.info(
                "No checkpoint yet for this chat."
            )

    except requests.RequestException:

        st.warning(
            "Checkpoint API unavailable."
        )


# ============================================================
# DISPLAY PREVIOUS CHAT
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )

        if (
            message["role"] == "assistant"
            and "result" in message
        ):

            result = message["result"]

            # ------------------------------------------------
            # APPROVAL
            # ------------------------------------------------

            if result.get("approval_id"):

                approval_id = result[
                    "approval_id"
                ]

                approval = get_approval_request(
                    approval_id
                )

                if approval:

                    status = approval["status"]

                    if status == "PENDING":

                        st.warning(
                            "⚠️ Human approval is required "
                            "before this action can run."
                        )

                        st.write(
                            f"**Tool:** "
                            f"`{approval['tool_name']}`"
                        )

                        st.write(
                            "**Arguments:**"
                        )

                        st.json(
                            approval["arguments"]
                        )

                        st.code(
                            approval_id,
                            language="text",
                        )

                        col1, col2 = st.columns(2)

                        with col1:

                            if st.button(
                                "✅ Approve",
                                key=f"approve_{approval_id}",
                            ):

                                try:

                                    approve_request(
                                        approval_id
                                    )

                                    execution = (
                                        execute_approved_request(
                                            approval_id
                                        )
                                    )

                                    st.success(
                                        "Action approved "
                                        "and executed successfully."
                                    )

                                    st.json(
                                        execution["result"]
                                    )

                                    st.rerun()

                                except RuntimeError as error:

                                    st.error(
                                        f"Approval execution failed: "
                                        f"{error}"
                                    )

                        with col2:

                            if st.button(
                                "❌ Reject",
                                key=f"reject_{approval_id}",
                            ):

                                st.error(
                                    "Request rejected."
                                )


            # ------------------------------------------------
            # LATENCY
            # ------------------------------------------------

            if result.get(
                "parallel_latency"
            ) is not None:

                with st.expander(
                    "⏱️ Detailed Latency"
                ):

                    st.write(
                        f"Sequential retrieval: "
                        f"**{result['sequential_latency']:.3f} seconds**"
                    )

                    st.write(
                        f"Parallel retrieval: "
                        f"**{result['parallel_latency']:.3f} seconds**"
                    )

                    st.write(
                        f"Latency reduction: "
                        f"**{result['reduction']:.3f} seconds**"
                    )

                    st.write(
                        f"Latency reduction percentage: "
                        f"**{result['reduction_percent']:.2f}%**"
                    )

                    st.write(
                        f"Speedup: "
                        f"**{result['speedup']:.2f}x**"
                    )

                    st.write(
                        f"Complete async benchmark latency: "
                        f"**{result['total_latency']:.3f} seconds**"
                    )


            # ------------------------------------------------
            # TOOLS
            # ------------------------------------------------

            if result.get("tools"):

                with st.expander(
                    "🔧 Tools Used"
                ):

                    display_tools(
                        result["tools"]
                    )


            # ------------------------------------------------
            # SOURCES
            # ------------------------------------------------

            if result.get("sources"):

                with st.expander(
                    "📚 Sources Cited"
                ):

                    display_sources(
                        result["sources"]
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
            "Running agent with checkpointing..."
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
        # ACTUAL AGENT ANSWER
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

            approval = get_approval_request(
                approval_id
            )

            if approval:

                st.warning(
                    "⚠️ Human approval is required "
                    "before this action can run."
                )

                st.write(
                    f"**Tool:** "
                    f"`{approval['tool_name']}`"
                )

                st.write(
                    "**Arguments:**"
                )

                st.json(
                    approval["arguments"]
                )

                st.write(
                    "**Approval ID:**"
                )

                st.code(
                    approval_id,
                    language="text",
                )


        # ----------------------------------------------------
        # TOOLS USED
        # ----------------------------------------------------

        tools_used = graph_result.get(
            "tools_used",
            [],
        )

        if tools_used:

            with st.expander(
                "🔧 Tools Used"
            ):

                for tool in tools_used:

                    st.markdown(
                        f"🔎 **`{tool}`**"
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
        # LATENCY DETAILS
        # ----------------------------------------------------

        with st.expander(
            "⏱️ Detailed Latency"
        ):

            st.write(
                f"Sequential retrieval: "
                f"**{sequential_latency:.3f} seconds**"
            )

            st.write(
                f"Parallel retrieval: "
                f"**{parallel_latency:.3f} seconds**"
            )

            st.write(
                f"Latency reduction: "
                f"**{reduction:.3f} seconds**"
            )

            st.write(
                f"Latency reduction percentage: "
                f"**{reduction_percent:.2f}%**"
            )

            st.write(
                f"Speedup: "
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
                        {
                            tool: ["LangGraph"]
                            for tool in tools_used
                        },

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
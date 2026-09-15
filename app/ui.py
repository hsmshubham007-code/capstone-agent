import asyncio
import uuid

import streamlit as st

from app.approval import (
    approve_request,
    execute_approved_request,
    get_approval_request,
    reject_request,
)
from app.async_tools import (
    run_tools_parallel,
    run_tools_sequential,
)
from app.audit import create_request_id
from app.graph import graph

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

        # ----------------------------------------------------
        # Detailed source dictionary
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # Simple source string
        # ----------------------------------------------------

        elif isinstance(source, str):

            st.markdown(
                f"📄 **{source}**"
            )

            st.write(
                "Source retrieved from the company "
                "policy knowledge base."
            )

        # ----------------------------------------------------
        # Unexpected source format
        # ----------------------------------------------------

        else:

            st.markdown(
                f"📄 **{source!s}**"
            )

        st.divider()


# ============================================================
# CHECKPOINT INFORMATION
# SIDEBAR ONLY
# ============================================================

with st.sidebar:

    st.header("💾 Checkpoint")

    st.write(
        "This chat uses a persistent LangGraph thread."
    )

    st.code(
        thread_id,
        language="text",
    )

    checkpoint = graph.get_state(
        {
            "configurable": {
                "thread_id": thread_id,
            }
        }
    )

    if checkpoint.values:

        st.success(
            "Checkpoint found"
        )

        st.write(
            f"Tool: "
            f"`{checkpoint.values.get('tool', '')}`"
        )

        st.write(
            f"Sources: "
            f"{len(checkpoint.values.get('sources', []))}"
        )

        st.write(
            f"Trace steps: "
            f"{len(checkpoint.values.get('trace', []))}"
        )

        approval_status = checkpoint.values.get(
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
            # APPROVAL INFORMATION
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

                                except Exception as error:  # noqa: BLE001

                                    st.error(
                                        f"Approval execution failed: "
                                        f"{error}"
                                    )

                        with col2:

                            if st.button(
                                "❌ Reject",
                                key=f"reject_{approval_id}",
                            ):

                                try:

                                    reject_request(
                                        approval_id
                                    )

                                    st.warning(
                                        "Action rejected. "
                                        "The risky tool was not executed."
                                    )

                                    st.rerun()

                                except Exception as error:  # noqa: BLE001

                                    st.error(
                                        f"Rejection failed: "
                                        f"{error}"
                                    )

                    elif status == "EXECUTED":

                        st.success(
                            "✅ This approved action "
                            "was executed."
                        )

                    elif status == "REJECTED":

                        st.error(
                            "❌ This action was rejected "
                            "and was not executed."
                        )

            # ------------------------------------------------
            # PERFORMANCE
            # ------------------------------------------------

            if "parallel_latency" in result:

                st.divider()

                st.subheader(
                    "⚡ Performance"
                )

                col1, col2, col3, col4 = st.columns(4)

                with col1:

                    st.metric(
                        "Parallel Retrieval",
                        f"{result['parallel_latency']:.3f} s",
                    )

                with col2:

                    st.metric(
                        "Sequential Retrieval",
                        f"{result['sequential_latency']:.3f} s",
                    )

                with col3:

                    st.metric(
                        "Latency Reduction",
                        f"{result['reduction_percent']:.2f}%",
                    )

                with col4:

                    st.metric(
                        "Speedup",
                        f"{result['speedup']:.2f}x",
                    )

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
                        f"Complete async agent latency: "
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

            # -----------------------------------------------
            # PERFORMANCE BENCHMARK
            # -----------------------------------------------

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

            # -----------------------------------------------
            # APPROVAL-AWARE LANGGRAPH EXECUTION
            # -----------------------------------------------

            request_id = create_request_id()

            initial_state = {

                "request_id":
                    request_id,

                "session_id":
                    thread_id,

                "question":
                    question,

                "conversation_history":
                    [],

                "tool":
                    "",

                "answer":
                    "",

                "sources":
                    [],

                "tools_used":
                    [],

                "approval_id":
                    "",

                "approval_status":
                    "",

                "trace":
                    [],
            }

            graph_result = graph.invoke(
                initial_state,
                config={
                    "configurable": {
                        "thread_id":
                            thread_id
                    }
                },
            )

        # ----------------------------------------------------
        # ACTUAL AGENT ANSWER
        # ----------------------------------------------------

        st.markdown(
            graph_result["answer"]
        )

        # ----------------------------------------------------
        # APPROVAL REQUIRED
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

                col1, col2 = st.columns(2)

                with col1:

                    if st.button(
                        "✅ Approve",
                        key=f"approve_new_{approval_id}",
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

                        except Exception as error:  # noqa: BLE001

                            st.error(
                                f"Execution failed: "
                                f"{error}"
                            )

                with col2:

                    if st.button(
                        "❌ Reject",
                        key=f"reject_new_{approval_id}",
                    ):

                        try:

                            reject_request(
                                approval_id
                            )

                            st.warning(
                                "Action rejected. "
                                "The risky tool was not executed."
                            )

                            st.rerun()

                        except Exception as error:  # noqa: BLE001

                            st.error(
                                f"Rejection failed: "
                                f"{error}"
                            )

        # ----------------------------------------------------
        # PERFORMANCE
        # ----------------------------------------------------

        st.divider()

        st.subheader(
            "⚡ Performance"
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                "Parallel Retrieval",
                f"{parallel_latency:.3f} s",
            )

        with col2:

            st.metric(
                "Sequential Retrieval",
                f"{sequential_latency:.3f} s",
            )

        with col3:

            st.metric(
                "Latency Reduction",
                f"{reduction_percent:.2f}%",
                delta=f"-{reduction:.3f} s",
            )

        with col4:

            st.metric(
                "Speedup",
                f"{speedup:.2f}x",
            )

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
        # TOOLS USED
        # ----------------------------------------------------

        if graph_result.get("tools_used"):

            with st.expander(
                "🔧 Tools Used"
            ):

                for tool in graph_result[
                    "tools_used"
                ]:

                    st.markdown(
                        f"🔎 **`{tool}`**"
                    )

        # ----------------------------------------------------
        # SOURCES
        # ----------------------------------------------------

        if graph_result.get("sources"):

            with st.expander(
                "📚 Sources Cited"
            ):

                display_sources(
                    graph_result["sources"]
                )

        # ----------------------------------------------------
        # SAVE MESSAGE
        # ----------------------------------------------------

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": graph_result["answer"],
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
                            tool: ["graph"]
                            for tool in graph_result.get(
                                "tools_used",
                                [],
                            )
                        },

                    "sources":
                        graph_result.get(
                            "sources",
                            [],
                        ),

                    "approval_id":
                        graph_result.get(
                            "approval_id",
                            "",
                        ),

                    "approval_status":
                        graph_result.get(
                            "approval_status",
                            "",
                        ),
                },
            }
        )
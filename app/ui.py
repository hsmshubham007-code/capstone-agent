import asyncio
import uuid

import streamlit as st

from app.graph import graph
from app.async_agent import async_agent
from app.async_tools import (
    run_tools_sequential,
    run_tools_parallel
)


st.set_page_config(
    page_title="Company Policy Agent",
    page_icon="🤖",
    layout="wide"
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

        st.markdown(
            f"📄 **{source['source']}**"
        )

        st.write(
            f"Page: `{source['page']}`"
        )

        st.write(
            f"Retrieval branch: `{source['tool']}`"
        )

        st.write(
            f"Similarity score: "
            f"`{source['score']:.4f}`"
        )

        st.divider()


# ============================================================
# CHECKPOINT INFORMATION
# ============================================================

with st.sidebar:

    st.header("💾 Checkpoint")

    st.write(
        "This chat uses a persistent LangGraph thread."
    )

    st.code(
        thread_id,
        language="text"
    )

    checkpoint = graph.get_state(
        {
            "configurable": {
                "thread_id": thread_id
            }
        }
    )

    if checkpoint.values:

        st.success(
            "Checkpoint found"
        )

        st.write(
            f"Tool: `{checkpoint.values.get('tool', '')}`"
        )

        st.write(
            f"Sources: "
            f"{len(checkpoint.values.get('sources', []))}"
        )

        st.write(
            f"Trace steps: "
            f"{len(checkpoint.values.get('trace', []))}"
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

            st.divider()

            st.subheader(
                "⚡ Performance"
            )

            col1, col2, col3, col4 = st.columns(4)

            with col1:

                st.metric(
                    "Parallel Retrieval",
                    f"{result['parallel_latency']:.3f} s"
                )

            with col2:

                st.metric(
                    "Sequential Retrieval",
                    f"{result['sequential_latency']:.3f} s"
                )

            with col3:

                st.metric(
                    "Latency Reduction",
                    f"{result['reduction_percent']:.2f}%"
                )

            with col4:

                st.metric(
                    "Speedup",
                    f"{result['speedup']:.2f}x"
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


            with st.expander(
                "🔧 Tools Used"
            ):

                display_tools(
                    result["tools"]
                )


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
    # USER MESSAGE
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )


    with st.chat_message("user"):

        st.markdown(
            question
        )


    # --------------------------------------------------------
    # ASSISTANT
    # --------------------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner(
            "Running agent with checkpointing..."
        ):

            # =================================================
            # PERFORMANCE TEST
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
            # EXISTING ASYNC AGENT
            # =================================================

            agent_result = asyncio.run(
                async_agent(
                    question
                )
            )


            # =================================================
            # LANGGRAPH CHECKPOINT
            # =================================================

            initial_state = {

                "session_id": thread_id,

                "question": question,

                "conversation_history": [],

                "tool": "",

                "answer": "",

                "sources": [],

                "tools_used": [],

                "trace": []
            }


            graph_result = graph.invoke(
                initial_state,
                config={
                    "configurable": {
                        "thread_id": thread_id
                    }
                }
            )


        # =====================================================
        # ANSWER
        # =====================================================

        st.markdown(
            agent_result["answer"]
        )


        st.divider()


        # =====================================================
        # CHECKPOINT STATUS
        # =====================================================

        st.subheader(
            "💾 Checkpoint"
        )

        checkpoint = graph.get_state(
            {
                "configurable": {
                    "thread_id": thread_id
                }
            }
        )


        col1, col2, col3 = st.columns(3)


        with col1:

            st.metric(
                "Checkpoint",
                "Saved"
            )


        with col2:

            st.metric(
                "Thread",
                thread_id[:8] + "..."
            )


        with col3:

            st.metric(
                "Graph Steps",
                len(
                    checkpoint.values.get(
                        "trace",
                        []
                    )
                )
            )


        # =====================================================
        # PERFORMANCE
        # =====================================================

        st.subheader(
            "⚡ Performance"
        )


        col1, col2, col3, col4 = st.columns(4)


        with col1:

            st.metric(
                "Parallel Retrieval",
                f"{parallel_latency:.3f} s"
            )


        with col2:

            st.metric(
                "Sequential Retrieval",
                f"{sequential_latency:.3f} s"
            )


        with col3:

            st.metric(
                "Latency Reduction",
                f"{reduction_percent:.2f}%",
                delta=f"-{reduction:.3f} s"
            )


        with col4:

            st.metric(
                "Speedup",
                f"{speedup:.2f}x"
            )


        # =====================================================
        # DETAILED LATENCY
        # =====================================================

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

            st.write(
                f"Complete async agent latency: "
                f"**{agent_result['total_latency']:.3f} seconds**"
            )


        # =====================================================
        # TOOLS
        # =====================================================

        with st.expander(
            "🔧 Tools Used"
        ):

            display_tools(
                agent_result["tools"]
            )


        # =====================================================
        # SOURCES
        # =====================================================

        with st.expander(
            "📚 Sources Cited"
        ):

            display_sources(
                agent_result["sources"]
            )


        # =====================================================
        # SAVE CHAT MESSAGE
        # =====================================================

        st.session_state.messages.append(
            {
                "role": "assistant",

                "content": agent_result["answer"],

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
                        agent_result[
                            "total_latency"
                        ],

                    "tools":
                        agent_result["tools"],

                    "sources":
                        agent_result["sources"]
                }
            }
        )
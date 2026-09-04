import uuid

import streamlit as st

from app.agent import run_agent


st.set_page_config(
    page_title="Company Policy Agent",
    page_icon="🤖",
    layout="wide"
)


if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []


st.title("🤖 Company Policy Agent")
st.caption("Ask questions about the company documents.")


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if message["role"] == "assistant":

            result = message.get("result")

            if result:

                if result["tools_used"]:
                    st.markdown("### 🔧 Tools Used")

                    for tool in result["tools_used"]:
                        st.write(f"- {tool}")

                if result["sources"]:
                    st.markdown("### 📚 Sources")

                    for source in result["sources"]:
                        st.write(f"- {source}")

                search_step = next(
                    (
                        step
                        for step in result["trace"]
                        if step["step"] == "search_documents"
                    ),
                    None
                )

                if search_step:
                    with st.expander("🔎 Retrieved Chunks"):
                        for i, item in enumerate(
                            search_step["results"],
                            1
                        ):
                            st.markdown(
                                f"**Chunk {i}** — "
                                f"`{item['source']}` — "
                                f"score: `{item['score']:.4f}`"
                            )

                            st.write(item["content"])

                with st.expander("🧭 Agent Trace"):
                    for step in result["trace"]:
                        st.write(
                            f"**{step['step']}** — "
                            f"{step['duration']:.3f}s"
                        )


question = st.chat_input(
    "Ask a question about company policies..."
)


if question:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            result = run_agent(
                question,
                session_id=st.session_state.session_id
            )

        st.markdown(result["answer"])

        if result["tools_used"]:
            st.markdown("### 🔧 Tools Used")

            for tool in result["tools_used"]:
                st.write(f"- {tool}")

        if result["sources"]:
            st.markdown("### 📚 Sources")

            for source in result["sources"]:
                st.write(f"- {source}")

        search_step = next(
            (
                step
                for step in result["trace"]
                if step["step"] == "search_documents"
            ),
            None
        )

        if search_step:
            with st.expander("🔎 Retrieved Chunks"):
                for i, item in enumerate(
                    search_step["results"],
                    1
                ):
                    st.markdown(
                        f"**Chunk {i}** — "
                        f"`{item['source']}` — "
                        f"score: `{item['score']:.4f}`"
                    )

                    st.write(item["content"])

        with st.expander("🧭 Agent Trace"):
            for step in result["trace"]:
                st.write(
                    f"**{step['step']}** — "
                    f"{step['duration']:.3f}s"
                )

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": result["answer"],
            "result": result
        }
    )


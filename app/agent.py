from app.audit import (
    create_request_id,
    record_tool_call,
)
from app.graph import graph
from app.guardrails import (
    detect_prompt_injection,
    validate_input,
    validate_output,
)
from app.memory import (
    add_message,
    get_history,
)


def run_agent(
    question,
    session_id="default",
):
    """
    Run the company policy agent.

    Every request receives a unique request_id.

    Safe tools can execute immediately.

    Risky tools are stopped and placed into
    the human approval queue.
    """

    # -------------------------------------------------
    # 1. Create request ID
    # -------------------------------------------------

    request_id = create_request_id()

    # -------------------------------------------------
    # 2. Validate user input
    # -------------------------------------------------

    question = validate_input(question)

    # -------------------------------------------------
    # 3. Prompt injection protection
    # -------------------------------------------------

    if detect_prompt_injection(question):

        record_tool_call(
            request_id=request_id,
            tool_name="guardrail",
            arguments={
                "question": question,
            },
            status="BLOCKED",
            outcome={
                "reason": "prompt_injection",
            },
        )

        return {
            "request_id": request_id,
            "question": question,
            "tool": "guardrail",
            "answer": (
                "I can't process requests that "
                "attempt to override the agent's "
                "instructions."
            ),
            "sources": [],
            "tools_used": [],
            "approval_id": "",
            "approval_status": "",
            "llm_metadata": None,
            "conversation_history": get_history(
                session_id
            ),
            "trace": [
                {
                    "step": "guardrail",
                    "tool": "guardrail",
                    "duration": 0,
                }
            ],
        }

    # -------------------------------------------------
    # 4. Get conversation history
    # -------------------------------------------------

    history = get_history(session_id)

    # -------------------------------------------------
    # 5. Create LangGraph state
    # -------------------------------------------------

    state = {
      "request_id": request_id,
      "session_id": session_id,
      "question": question,
      "conversation_history": history,
      "tool": "",
      "answer": "",
      "sources": [],
      "tools_used": [],
      "approval_id": "",
      "approval_status": "",
      "llm_metadata": None,
      "trace": [],
    }

    # -------------------------------------------------
    # 6. Run LangGraph
    # -------------------------------------------------

    result = graph.invoke(
        state,
        config={
            "configurable": {
                "thread_id": session_id,
            }
        },
    )

    # -------------------------------------------------
    # 7. Validate final answer
    # -------------------------------------------------

    result["answer"] = validate_output(
        result["answer"]
    )

    # -------------------------------------------------
    # 8. Store conversation memory
    # -------------------------------------------------

    add_message(
        session_id,
        "user",
        question,
    )

    add_message(
        session_id,
        "assistant",
        result["answer"],
    )

    result["conversation_history"] = get_history(
        session_id
    )

    # -------------------------------------------------
    # 9. Make sure request ID is returned
    # -------------------------------------------------

    result["request_id"] = request_id

    # -------------------------------------------------
    # 10. Determine approval status
    # -------------------------------------------------

    if result.get("approval_id"):

        result["approval_status"] = "PENDING"

    else:

        result["approval_status"] = ""

    return result


if __name__ == "__main__":

    session_id = "demo"

    while True:

        question = input("\nYou: ")

        if question.lower() == "exit":
            break

        try:

            result = run_agent(
                question,
                session_id,
            )

            print("\nAssistant:")
            print(result["answer"])

            # -----------------------------------------
            # Request ID
            # -----------------------------------------

            print("\nRequest ID:")
            print(result["request_id"])

            # -----------------------------------------
            # Approval information
            # -----------------------------------------

            if result.get("approval_id"):

                print("\n⚠️ APPROVAL REQUIRED")

                print(
                    "Approval ID:"
                )

                print(
                    result["approval_id"]
                )

                print(
                    "Approval Status:"
                )

                print(
                    result["approval_status"]
                )

            # -----------------------------------------
            # Tools
            # -----------------------------------------

            print("\nTools Used:")

            for tool in result["tools_used"]:

                print(
                    f"- {tool}"
                )

            # -----------------------------------------
            # Sources
            # -----------------------------------------

            print("\nSources:")

            for source in result["sources"]:

                print(
                    f"- {source}"
                )

            # -----------------------------------------
            # Retrieval details
            # -----------------------------------------

            print("\nRetrieval:")

            search_step = next(
                (
                    step
                    for step in result["trace"]
                    if step["step"]
                    == "search_documents"
                ),
                None,
            )

            if search_step:

                for i, item in enumerate(
                    search_step["results"],
                    1,
                ):

                    print(
                        f"\n--- Retrieved Chunk {i} ---"
                    )

                    print(
                        f"Source : "
                        f"{item['source']}"
                    )

                    print(
                        f"Score  : "
                        f"{item['score']:.4f}"
                    )

                    print(
                        f"Content: "
                        f"{item['content']}"
                    )

            # -----------------------------------------
            # Trace
            # -----------------------------------------

            print("\nTrace:")

            for step in result["trace"]:

                duration = step.get(
                    "duration",
                    0,
                )

                print(
                    f"- {step['step']} "
                    f"({duration:.3f}s)"
                )

                if step.get(
                    "approval_id"
                ):

                    print(
                        f"  Approval ID: "
                        f"{step['approval_id']}"
                    )

                if step.get(
                    "status"
                ):

                    print(
                        f"  Status: "
                        f"{step['status']}"
                    )

        except Exception as error:  # noqa: BLE001

            print(
                "\nAgent error:"
            )

            print(
                str(error)
            )


from app.graph import graph
from app.guardrails import (
    detect_prompt_injection,
    validate_input,
    validate_output,
)
from app.memory import add_message, get_history


def run_agent(question, session_id="default"):
    question = validate_input(question)

    if detect_prompt_injection(question):
        return {
            "question": question,
            "tool": "guardrail",
            "answer": "I can't process requests that attempt to override the agent's instructions.",
            "sources": [],
            "tools_used": [],
            "conversation_history": get_history(session_id),
            "trace": [
                {
                    "step": "guardrail",
                    "tool": "guardrail",
                    "duration": 0
                }
            ]
        }

    history = get_history(session_id)

    state = {
        "session_id": session_id,
        "question": question,
        "conversation_history": history,
        "tool": "",
        "answer": "",
        "sources": [],
        "tools_used": [],
        "trace": []
    }

    result = graph.invoke(state)

    result["answer"] = validate_output(result["answer"])

    add_message(session_id, "user", question)
    add_message(session_id, "assistant", result["answer"])

    result["conversation_history"] = get_history(session_id)

    return result


if __name__ == "__main__":
    session_id = "demo"

    while True:
        question = input("\nYou: ")

        if question.lower() == "exit":
            break

        result = run_agent(question, session_id)

        print("\nAssistant:")
        print(result["answer"])

        print("\nTools Used:")
        for tool in result["tools_used"]:
            print(f"- {tool}")

        print("\nSources:")
        for source in result["sources"]:
            print(f"- {source}")

        print("\nRetrieval:")

        search_step = next(
            (
                step
                for step in result["trace"]
                if step["step"] == "search_documents"
            ),
            None
        )

        if search_step:
            for i, item in enumerate(search_step["results"], 1):
                print(f"\n--- Retrieved Chunk {i} ---")
                print(f"Source : {item['source']}")
                print(f"Score  : {item['score']:.4f}")
                print(f"Content: {item['content']}")

        print("\nTrace:")

        for step in result["trace"]:
            print(
                f"- {step['step']} "
                f"({step['duration']:.3f}s)"
            )


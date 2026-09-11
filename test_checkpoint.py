from app.graph import graph


initial_state = {
    "session_id": "checkpoint-test",
    "question": "What are the rules for professional conduct?",
    "conversation_history": [],
    "tool": "",
    "answer": "",
    "sources": [],
    "tools_used": [],
    "trace": []
}


config = {
    "configurable": {
        "thread_id": "demo-thread-001"
    }
}


print("=" * 70)
print("RUNNING LANGGRAPH WITH DURABLE CHECKPOINTING")
print("=" * 70)


result = graph.invoke(
    initial_state,
    config=config
)


print("\nANSWER")
print("-" * 70)

print(result["answer"])


print("\nTOOLS USED")
print("-" * 70)

for tool in result["tools_used"]:
    print("-", tool)


print("\nSOURCES")
print("-" * 70)

for source in result["sources"]:
    print("-", source)


print("\nTRACE")
print("-" * 70)

for step in result["trace"]:
    print(step)


print("\nCHECKPOINT THREAD")
print("-" * 70)

print(config["configurable"]["thread_id"])


print("\nCHECKPOINTING TEST COMPLETE")
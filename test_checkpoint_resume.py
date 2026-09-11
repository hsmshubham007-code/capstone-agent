from app.graph import graph


THREAD_ID = "resume-test-001"


config = {
    "configurable": {
        "thread_id": THREAD_ID
    }
}


print("=" * 70)
print("CHECKPOINT RESUME TEST")
print("=" * 70)


# --------------------------------------------------
# 1. First run
# --------------------------------------------------

initial_state = {
    "session_id": THREAD_ID,
    "question": "What are the rules for professional conduct?",
    "conversation_history": [],
    "tool": "",
    "answer": "",
    "sources": [],
    "tools_used": [],
    "trace": []
}


print("\n1. Running first execution...")

result = graph.invoke(
    initial_state,
    config=config
)


print("\nFirst execution completed.")

print("\nAnswer:")
print(result["answer"])


# --------------------------------------------------
# 2. Read persisted checkpoint
# --------------------------------------------------

print("\n" + "=" * 70)
print("2. READING PERSISTED CHECKPOINT")
print("=" * 70)


checkpoint = graph.get_state(config)


print("\nThread ID:")
print(
    checkpoint.config["configurable"]["thread_id"]
)


print("\nCheckpoint ID:")
print(
    checkpoint.config["configurable"]["checkpoint_id"]
)


print("\nPersisted question:")
print(
    checkpoint.values["question"]
)


print("\nPersisted tool:")
print(
    checkpoint.values["tool"]
)


print("\nPersisted answer exists:")
print(
    bool(checkpoint.values["answer"])
)


print("\nPersisted sources:")
print(
    checkpoint.values["sources"]
)


print("\nPersisted trace:")

for step in checkpoint.values["trace"]:
    print(step)


print("\n" + "=" * 70)
print("CHECKPOINT RESUME TEST PASSED")
print("=" * 70)
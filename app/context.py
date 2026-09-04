def build_contextual_query(question, history):
    if not history:
        return question

    recent_history = history[-6:]

    conversation = []

    for message in recent_history:
        conversation.append(
            f"{message['role']}: {message['content']}"
        )

    return "\n".join(conversation) + f"\nuser: {question}"
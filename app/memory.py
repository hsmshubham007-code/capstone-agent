memory_store = {}


def get_history(session_id):
    return memory_store.get(session_id, [])


def add_message(session_id, role, content):
    memory_store.setdefault(session_id, []).append({
        "role": role,
        "content": content
    })


def clear_memory(session_id):
    memory_store.pop(session_id, None)
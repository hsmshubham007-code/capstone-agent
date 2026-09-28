from app.audit import (
    create_request_id,
    get_request_events,
    record_tool_call,
)


def main():
    request_id = create_request_id()

    print("Request ID:", request_id)

    record_tool_call(
        request_id=request_id,
        tool_name="search_policy",
        arguments={
            "query": "leave policy"
        },
        status="SUCCESS",
        outcome={
            "documents_found": 4
        },
    )

    events = get_request_events(request_id)

    print("\nAudit events:")
    print("=" * 60)

    for event in events:
        print(event)

    print("=" * 60)
    print("Total events:", len(events))


if __name__ == "__main__":
    main()
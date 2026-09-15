from app.approval import (
    approve_request,
    create_approval_request,
    get_pending_approvals,
)


def main():

    approval = create_approval_request(
        request_id="test-request-001",
        tool_name="update_employee_record",
        arguments={
            "employee_id": "EMP102",
            "field": "salary",
            "new_value": 80000,
        },
    )

    print("\nApproval created:")
    print("=" * 60)
    print(approval)
    print("=" * 60)

    print("\nPending approvals:")

    for item in get_pending_approvals():
        print(item)

    print("\nApproving request...")

    approved = approve_request(
        approval["approval_id"]
    )

    print(approved)


if __name__ == "__main__":
    main()
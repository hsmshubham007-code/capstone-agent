from app.approval import (
    approve_request,
    create_approval_request,
    execute_approved_request,
)


def test_delete_approval_execution_flow():
    approval = create_approval_request(
        request_id="test-delete-001",
        tool_name="delete_employee_record",
        arguments={
            "employee_id": "EMP102",
        },
    )

    assert approval["status"] == "PENDING"

    approved = approve_request(
        approval["approval_id"]
    )

    assert approved["status"] == "APPROVED"

    result = execute_approved_request(
        approval["approval_id"]
    )

    assert result["approval"]["status"] == "EXECUTED"

    assert result["result"]["success"] is True

    assert result["result"]["employee_id"] == "EMP102"
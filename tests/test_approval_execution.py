from app.approval import (
    approve_request,
    create_approval_request,
    execute_approved_request,
)


def test_approval_execution_flow():
    approval = create_approval_request(
        request_id="test-execution-001",
        tool_name="update_employee_record",
        arguments={
            "employee_id": "EMP102",
            "field": "salary",
            "new_value": 80000,
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
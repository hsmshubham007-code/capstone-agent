import pytest

from app.approval import (
    approve_request,
    create_approval_request,
    execute_approved_request,
    reject_request,
)


def create_test_request(request_id="safety-test-001"):
    return create_approval_request(
        request_id=request_id,
        tool_name="update_employee_record",
        arguments={
            "employee_id": "EMP102",
            "field": "salary",
            "new_value": 80000,
        },
    )


def test_pending_request_cannot_execute():
    approval = create_test_request()

    with pytest.raises(ValueError):
        execute_approved_request(approval["approval_id"])


def test_rejected_request_cannot_execute():
    approval = create_test_request("safety-test-rejected")

    rejected = reject_request(approval["approval_id"])

    assert rejected["status"] == "REJECTED"

    with pytest.raises(ValueError):
        execute_approved_request(approval["approval_id"])


def test_approved_request_can_execute():
    approval = create_test_request("safety-test-approved")

    approved = approve_request(approval["approval_id"])

    assert approved["status"] == "APPROVED"

    result = execute_approved_request(approval["approval_id"])

    assert result["approval"]["status"] == "EXECUTED"
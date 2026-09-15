from app.approval import (
    approve_request,
    create_approval_request,
    execute_approved_request,
)

print("\n1. Creating approval request...")

approval = create_approval_request(
    request_id="test-execution-001",
    tool_name="update_employee_record",
    arguments={
        "employee_id": "EMP102",
        "field": "salary",
        "new_value": 80000,
    },
)

print("\nApproval created:")
print(approval)


print("\n2. Approving request...")

approved = approve_request(
    approval["approval_id"]
)

print("\nApproval after approval:")
print(approved)


print("\n3. Executing approved request...")

result = execute_approved_request(
    approval["approval_id"]
)

print("\nExecution result:")
print(result)


print("\n4. Final approval status:")

print(
    result["approval"]["status"]
)
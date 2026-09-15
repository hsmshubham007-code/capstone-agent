from app.approval import (
    approve_request,
    create_approval_request,
    execute_approved_request,
    reject_request,
)


def create_test_request():
    return create_approval_request(
        request_id="safety-test-001",
        tool_name="update_employee_record",
        arguments={
            "employee_id": "EMP102",
            "field": "salary",
            "new_value": 80000,
        },
    )


print("\n========================================")
print("TEST 1: PENDING REQUEST")
print("========================================")

approval = create_test_request()

print("Status:", approval["status"])

try:
    execute_approved_request(
        approval["approval_id"]
    )

    print("❌ SECURITY FAILURE")
    print("Pending request was executed!")

except ValueError as error:

    print("✅ PASS")
    print("Execution blocked:")
    print(error)


print("\n========================================")
print("TEST 2: REJECTED REQUEST")
print("========================================")

approval = create_test_request()

rejected = reject_request(
    approval["approval_id"]
)

print("Status:", rejected["status"])

try:
    execute_approved_request(
        approval["approval_id"]
    )

    print("❌ SECURITY FAILURE")
    print("Rejected request was executed!")

except ValueError as error:

    print("✅ PASS")
    print("Execution blocked:")
    print(error)


print("\n========================================")
print("TEST 3: APPROVED REQUEST")
print("========================================")

approval = create_test_request()

approved = approve_request(
    approval["approval_id"]
)

print("Status:", approved["status"])

try:

    result = execute_approved_request(
        approval["approval_id"]
    )

    print("✅ PASS")
    print("Tool executed successfully.")
    print("Final status:")
    print(result["approval"]["status"])

except (KeyError, ValueError, RuntimeError) as error:

    print("❌ FAILURE")
    print(error)


print("\n========================================")
print("SAFETY TEST COMPLETE")
print("========================================")
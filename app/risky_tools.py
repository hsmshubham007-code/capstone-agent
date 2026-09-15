from app.audit import record_tool_call


def update_employee_record(
    request_id: str,
    employee_id: str,
    field: str,
    new_value,
):
    """
    Simulated risky tool.

    This represents a destructive/mutating action.
    It only runs after human approval.
    """

    record_tool_call(
        request_id=request_id,
        tool_name="update_employee_record",
        arguments={
            "employee_id": employee_id,
            "field": field,
            "new_value": new_value,
        },
        status="STARTED",
    )

    try:

        # This is intentionally simulated.
        # We are NOT changing a real employee database.

        result = {
            "success": True,
            "employee_id": employee_id,
            "field": field,
            "new_value": new_value,
            "message": (
                "Employee record updated successfully "
                "(simulated)."
            ),
        }

        record_tool_call(
            request_id=request_id,
            tool_name="update_employee_record",
            arguments={
                "employee_id": employee_id,
                "field": field,
                "new_value": new_value,
            },
            status="SUCCESS",
            outcome=result,
        )

        return result

    except Exception as error:

        record_tool_call(
            request_id=request_id,
            tool_name="update_employee_record",
            arguments={
                "employee_id": employee_id,
                "field": field,
                "new_value": new_value,
            },
            status="FAILED",
            error=str(error),
        )

        raise
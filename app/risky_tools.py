from app.audit import record_tool_call


def update_employee_record(
    request_id: str,
    employee_id: str,
    field: str,
    new_value,
) -> dict:
    """Simulate an employee-record update after approval."""

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
        result = {
            "success": True,
            "employee_id": employee_id,
            "field": field,
            "new_value": new_value,
            "message": "Employee record updated successfully.",
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

    except Exception as exc:
        record_tool_call(
            request_id=request_id,
            tool_name="update_employee_record",
            arguments={
                "employee_id": employee_id,
                "field": field,
                "new_value": new_value,
            },
            status="FAILED",
            error=str(exc),
        )
        raise


def delete_employee_record(
    request_id: str,
    employee_id: str,
) -> dict:
    """Simulate deleting an employee record after approval."""

    record_tool_call(
        request_id=request_id,
        tool_name="delete_employee_record",
        arguments={
            "employee_id": employee_id,
        },
        status="STARTED",
    )

    try:
        result = {
            "success": True,
            "employee_id": employee_id,
            "message": "Employee record deleted successfully.",
        }

        record_tool_call(
            request_id=request_id,
            tool_name="delete_employee_record",
            arguments={
                "employee_id": employee_id,
            },
            status="SUCCESS",
            outcome=result,
        )

        return result

    except Exception as exc:
        record_tool_call(
            request_id=request_id,
            tool_name="delete_employee_record",
            arguments={
                "employee_id": employee_id,
            },
            status="FAILED",
            error=str(exc),
        )
        raise
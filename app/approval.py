from app.audit import record_approval_event

approval_queue = {}


def create_approval_request(
    request_id: str,
    tool_name: str,
    arguments: dict,
) -> dict:
    """Create a pending approval request."""

    approval_id = f"approval-{len(approval_queue) + 1}"

    approval = {
        "approval_id": approval_id,
        "request_id": request_id,
        "tool_name": tool_name,
        "arguments": arguments,
        "status": "PENDING",
        "result": None,
    }

    approval_queue[approval_id] = approval

    record_approval_event(
        request_id=request_id,
        approval_id=approval_id,
        tool_name=tool_name,
        status="PENDING",
        details={
            "action": "APPROVAL_CREATED",
            "arguments": arguments,
        },
    )

    return approval


def get_approval_request(
    approval_id: str,
) -> dict | None:
    """Return an approval request by ID."""

    return approval_queue.get(approval_id)


def get_pending_approvals() -> list[dict]:
    """Return all pending approval requests."""

    return [
        approval
        for approval in approval_queue.values()
        if approval["status"] == "PENDING"
    ]


def approve_request(
    approval_id: str,
) -> dict:
    """Approve a pending request."""

    approval = get_approval_request(approval_id)

    if approval is None:
        raise ValueError(
            f"Approval request not found: {approval_id}"
        )

    if approval["status"] != "PENDING":
        raise ValueError(
            "Only PENDING approval requests can be approved. "
            f"Current status: {approval['status']}"
        )

    approval["status"] = "APPROVED"

    record_approval_event(
        request_id=approval["request_id"],
        approval_id=approval_id,
        tool_name=approval["tool_name"],
        status="APPROVED",
        details={
            "action": "APPROVAL_APPROVED",
        },
    )

    return approval


def reject_request(
    approval_id: str,
) -> dict:
    """Reject a pending request."""

    approval = get_approval_request(approval_id)

    if approval is None:
        raise ValueError(
            f"Approval request not found: {approval_id}"
        )

    if approval["status"] != "PENDING":
        raise ValueError(
            "Only PENDING approval requests can be rejected. "
            f"Current status: {approval['status']}"
        )

    approval["status"] = "REJECTED"

    record_approval_event(
        request_id=approval["request_id"],
        approval_id=approval_id,
        tool_name=approval["tool_name"],
        status="REJECTED",
        details={
            "action": "APPROVAL_REJECTED",
        },
    )

    return approval


def execute_approved_request(
    approval_id: str,
) -> dict:
    """Execute an approved risky tool."""

    approval = get_approval_request(approval_id)

    if approval is None:
        raise ValueError(
            f"Approval request not found: {approval_id}"
        )

    if approval["status"] != "APPROVED":
        raise ValueError(
            "Approval request must be APPROVED before execution. "
            f"Current status: {approval['status']}"
        )

    tool_name = approval["tool_name"]
    arguments = approval["arguments"]

    # -------------------------------------------------
    # Update employee record
    # -------------------------------------------------

    if tool_name == "update_employee_record":
        from app.risky_tools import update_employee_record

        result = update_employee_record(
            request_id=approval["request_id"],
            employee_id=arguments["employee_id"],
            field=arguments["field"],
            new_value=arguments["new_value"],
        )

    # -------------------------------------------------
    # Delete employee record
    # -------------------------------------------------

    elif tool_name == "delete_employee_record":
        from app.risky_tools import delete_employee_record

        result = delete_employee_record(
            request_id=approval["request_id"],
            employee_id=arguments["employee_id"],
        )

    # -------------------------------------------------
    # Unsupported risky tool
    # -------------------------------------------------

    else:
        raise ValueError(
            f"Unsupported approved tool: {tool_name}"
        )

    approval["status"] = "EXECUTED"
    approval["result"] = result

    record_approval_event(
        request_id=approval["request_id"],
        approval_id=approval_id,
        tool_name=tool_name,
        status="EXECUTED",
        details={
            "action": "APPROVAL_EXECUTED",
            "result": result,
        },
    )

    return {
        "approval": approval,
        "result": result,
    }
import uuid
from datetime import datetime, timezone

from app.audit import record_approval_event

approval_queue = {}


def _utc_now():
    """Return the current UTC timestamp."""
    return datetime.now(timezone.utc).isoformat()


def create_approval_request(
    request_id: str,
    tool_name: str,
    arguments: dict,
):
    """
    Create a new approval request for a risky tool.
    """

    approval_id = str(uuid.uuid4())

    now = _utc_now()

    approval = {
        "approval_id": approval_id,
        "request_id": request_id,
        "tool_name": tool_name,
        "arguments": arguments,
        "status": "PENDING",
        "created_at": now,
        "updated_at": now,
    }

    approval_queue[approval_id] = approval

    record_approval_event(
        request_id=request_id,
        approval_id=approval_id,
        tool_name=tool_name,
        status="PENDING",
        details={
            "arguments": arguments,
        },
    )

    return approval


def get_approval_request(
    approval_id: str,
):
    """
    Get one approval request by ID.
    """

    return approval_queue.get(approval_id)


def get_pending_approvals():
    """
    Return all approval requests waiting
    for human approval.
    """

    return [
        approval
        for approval in approval_queue.values()
        if approval["status"] == "PENDING"
    ]


def approve_request(
    approval_id: str,
):
    """
    Approve a pending request.

    Important:
    Approval does NOT execute the tool.
    Execution happens separately through
    execute_approved_request().
    """

    approval = approval_queue.get(
        approval_id
    )

    if not approval:
        raise ValueError(
            f"Approval request not found: "
            f"{approval_id}"
        )

    if approval["status"] != "PENDING":
        raise ValueError(
            f"Approval request is already "
            f"{approval['status']}"
        )

    approval["status"] = "APPROVED"
    approval["updated_at"] = _utc_now()

    record_approval_event(
        request_id=approval["request_id"],
        approval_id=approval_id,
        tool_name=approval["tool_name"],
        status="APPROVED",
        details={
            "arguments": approval["arguments"],
        },
    )

    return approval


def reject_request(
    approval_id: str,
):
    """
    Reject a pending request.

    Rejected requests can NEVER be executed.
    """

    approval = approval_queue.get(
        approval_id
    )

    if not approval:
        raise ValueError(
            f"Approval request not found: "
            f"{approval_id}"
        )

    if approval["status"] != "PENDING":
        raise ValueError(
            f"Approval request is already "
            f"{approval['status']}"
        )

    approval["status"] = "REJECTED"
    approval["updated_at"] = _utc_now()

    record_approval_event(
        request_id=approval["request_id"],
        approval_id=approval_id,
        tool_name=approval["tool_name"],
        status="REJECTED",
        details={
            "arguments": approval["arguments"],
        },
    )

    return approval


def execute_approved_request(
    approval_id: str,
):
    """
    Execute a risky tool ONLY after approval.

    Safety rules:

    1. Approval request must exist.
    2. Status must be APPROVED.
    3. Tool must be explicitly supported.
    4. Stored arguments are used.
    5. Rejected/PENDING requests cannot execute.
    """

    approval = approval_queue.get(
        approval_id
    )

    if not approval:
        raise ValueError(
            f"Approval request not found: "
            f"{approval_id}"
        )

    if approval["status"] != "APPROVED":
        raise ValueError(
            "Request cannot be executed. "
            f"Current status: {approval['status']}"
        )

    tool_name = approval["tool_name"]
    arguments = approval["arguments"]

    # -------------------------------------------------
    # Explicit tool allow-list
    # -------------------------------------------------

    if tool_name == "update_employee_record":

        # Lazy import avoids circular imports.
        from app.risky_tools import update_employee_record

        result = update_employee_record(
            request_id=approval["request_id"],
            employee_id=arguments["employee_id"],
            field=arguments["field"],
            new_value=arguments["new_value"],
        )

    else:

        raise ValueError(
            f"Unsupported approved tool: "
            f"{tool_name}"
        )

    # -------------------------------------------------
    # Mark approval as executed
    # -------------------------------------------------

    approval["status"] = "EXECUTED"
    approval["updated_at"] = _utc_now()

    record_approval_event(
        request_id=approval["request_id"],
        approval_id=approval_id,
        tool_name=tool_name,
        status="EXECUTED",
        details={
            "arguments": arguments,
            "result": result,
        },
    )

    return {
        "approval": approval,
        "result": result,
    }
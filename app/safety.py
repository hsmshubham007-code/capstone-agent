# Tools that can change, delete, send, or otherwise
# modify something must require human approval.

RISKY_TOOLS = {
    "update_employee_record",
    "delete_employee_record",
    "send_email",
    "change_company_policy",
}


def requires_approval(tool_name: str) -> bool:
    """
    Return True when a tool requires human approval.
    """

    return tool_name in RISKY_TOOLS
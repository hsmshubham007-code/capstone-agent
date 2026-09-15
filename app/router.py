def decide_tool(
    question: str,
    history=None,
):
    """
    Decide which tool should handle the request.

    Available tools:

    - search_documents
    - update_employee_record
    - no_tool

    Risky tools are NOT executed here.
    The graph sends risky tools to the approval gate.
    """

    question_lower = question.lower().strip()

    # -------------------------------------------------
    # 1. Risky employee-record operations
    # -------------------------------------------------

    employee_update_keywords = [
        "update employee",
        "update the employee",
        "change employee",
        "change the employee",
        "update employee record",
        "change employee record",
        "employee record",
        "update salary",
        "change salary",
        "increase salary",
        "decrease salary",
        "modify salary",
    ]

    if any(
        keyword in question_lower
        for keyword in employee_update_keywords
    ):
        return "update_employee_record"

    # -------------------------------------------------
    # 2. Company policy / document questions
    # -------------------------------------------------

    policy_keywords = [
        # General policy terms
        "policy",
        "policies",
        "company policy",
        "company policies",
        "company rules",
        "rules",
        "guidelines",
        "procedure",
        "procedures",

        # HR
        "leave",
        "holiday",
        "holidays",
        "hr policy",
        "hr",
        "employee benefits",
        "benefits",
        "remote work",
        "hybrid work",
        "attendance",
        "resignation",
        "notice period",
        "employee conduct",
        "professional conduct",
        "workplace conduct",
        "code of conduct",

        # IT / Security
        "security policy",
        "security policies",
        "security procedures",
        "password policy",
        "password policies",
        "it policy",
        "it policies",
        "acceptable use",
        "access control",
        "data security",
        "information security",

        # Company document language
        "company says",
        "company's policy",
        "company policy says",
        "according to company policy",
        "according to the policy",

        # Common policy subjects
        "laptop",
        "laptops",
        "equipment",
        "work from home",
        "wfh",
        "working hours",
        "work hours",
        "attendance policy",
        "vacation",
        "time off",
        "notice",
        "disciplinary",
        "discipline",
        "confidentiality",
        "confidential information",
    ]

    if any(
        keyword in question_lower
        for keyword in policy_keywords
    ):
        return "search_documents"

    # -------------------------------------------------
    # 3. Follow-up questions
    # -------------------------------------------------

    if history:
        followup_keywords = [
            "tell me that again",
            "tell me again",
            "repeat that",
            "repeat it",
            "what did you say",
            "can you repeat",
            "that again",
            "more details",
            "explain that",
            "explain it",
            "what about that",
        ]

        if any(
            keyword in question_lower
            for keyword in followup_keywords
        ):
            return "search_documents"

    # -------------------------------------------------
    # 4. Nothing appropriate
    # -------------------------------------------------

    return "no_tool"
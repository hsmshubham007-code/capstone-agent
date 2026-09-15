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

        # Workplace behavior
        "harassment",
        "workplace harassment",
        "sexual harassment",
        "discrimination",
        "bullying",
        "violence",
        "threat",
        "inappropriate behavior",
        "misconduct",
        "grievance",
        "complaint",
        "report harassment",

        # Reporting / compliance
        "policy violation",
        "policy violations",
        "violation",
        "violations",
        "report a violation",
        "report violations",
        "reporting a violation",
        "reporting violations",
        "report it",
        "reporting",
        "non-retaliation",
        "retaliation",
        "compliance",
        "compliant",

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
        "cybersecurity",
        "security",
        "data protection",
        "protect data",
        "protect information",
        "protect company information",
        "company information",
        "confidentiality",
        "confidential information",
        "sensitive information",
        "information protection",

        # Company document language
        "company says",
        "company's policy",
        "company policy says",
        "according to company policy",
        "according to the policy",
        "according to company rules",

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
        "training",
        "employee responsibilities",
        "employee responsibility",
    ]

    if any(
        keyword in question_lower
        for keyword in policy_keywords
    ):
        return "search_documents"

    # -------------------------------------------------
    # 3. Natural-language policy questions
    # -------------------------------------------------

    # Some policy questions do not contain the word
    # "policy". These patterns catch common questions
    # about employee/company rules.

    question_patterns = [
        "what should employees do",
        "what must employees do",
        "what are employees expected to do",
        "what can employees do",
        "what should i do",
        "what must i do",
        "how should employees",
        "how must employees",
        "how can employees",
        "what happens if an employee",
        "what happens if i",
        "are employees allowed",
        "is an employee allowed",
        "can employees",
        "can i",
        "must employees",
        "do employees need to",
        "are we allowed to",
        "am i allowed to",
    ]

    if any(
        pattern in question_lower
        for pattern in question_patterns
    ):
        # Avoid routing obviously external questions
        # such as stock prices or weather to the RAG tool.
        external_keywords = [
            "stock price",
            "share price",
            "weather",
            "news",
            "current price",
            "market price",
            "bitcoin",
            "cryptocurrency",
            "sports score",
            "cricket score",
            "football score",
        ]

        if not any(
            keyword in question_lower
            for keyword in external_keywords
        ):
            return "search_documents"

    # -------------------------------------------------
    # 4. Follow-up questions
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
            "can you explain",
            "please explain",
        ]

        if any(
            keyword in question_lower
            for keyword in followup_keywords
        ):
            return "search_documents"

    # -------------------------------------------------
    # 5. Nothing appropriate
    # -------------------------------------------------

    return "no_tool"
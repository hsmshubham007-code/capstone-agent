from app.safety import requires_approval


def main():

    tests = [
        "search_documents",
        "update_employee_record",
        "delete_employee_record",
        "send_email",
    ]

    for tool in tests:

        print(
            f"{tool}: "
            f"approval_required="
            f"{requires_approval(tool)}"
        )


if __name__ == "__main__":
    main()
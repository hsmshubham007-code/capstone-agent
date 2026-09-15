from app.safety import requires_approval


def test_search_documents_does_not_require_approval():
    assert requires_approval("search_documents") is False


def test_update_employee_record_requires_approval():
    assert requires_approval("update_employee_record") is True


def test_send_email_requires_approval():
    assert requires_approval("send_email") is True
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

AUDIT_DIR = Path("audit_logs")
AUDIT_FILE = AUDIT_DIR / "audit.jsonl"


def _ensure_audit_directory():
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)


def create_request_id() -> str:
    """Create a unique ID for one user request."""
    return str(uuid.uuid4())


def record_tool_call(
    request_id: str,
    tool_name: str,
    arguments: dict[str, Any] | None = None,
    status: str = "STARTED",
    outcome: Any = None,
    error: str | None = None,
):
    """
    Record one tool-call event in the audit trail.
    """

    _ensure_audit_directory()

    event = {
        "event_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "request_id": request_id,
        "event_type": "tool_call",
        "tool_name": tool_name,
        "arguments": arguments or {},
        "status": status,
        "outcome": outcome,
        "error": error,
    }

    with AUDIT_FILE.open("a", encoding="utf-8") as file:
        file.write(json.dumps(event, default=str) + "\n")

    return event


def record_approval_event(
    request_id: str,
    approval_id: str,
    tool_name: str,
    status: str,
    details: dict[str, Any] | None = None,
):
    """
    Record approval queue events.
    """

    _ensure_audit_directory()

    event = {
        "event_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "request_id": request_id,
        "event_type": "approval",
        "approval_id": approval_id,
        "tool_name": tool_name,
        "status": status,
        "details": details or {},
    }

    with AUDIT_FILE.open("a", encoding="utf-8") as file:
        file.write(json.dumps(event, default=str) + "\n")

    return event


def record_security_event(
    request_id: str,
    event_type: str,
    status: str,
    details: dict[str, Any] | None = None,
):
    """
    Record a security-related event in the audit trail.

    Examples:
        PROMPT_INJECTION_DETECTED
        INPUT_REJECTED
        OUTPUT_VALIDATION_FAILED
    """

    _ensure_audit_directory()

    event = {
        "event_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "request_id": request_id,
        "event_type": "security",
        "security_event": event_type,
        "status": status,
        "details": details or {},
    }

    with AUDIT_FILE.open("a", encoding="utf-8") as file:
        file.write(json.dumps(event, default=str) + "\n")

    return event


def get_audit_events():
    """
    Read all audit events.
    """

    if not AUDIT_FILE.exists():
        return []

    events = []

    with AUDIT_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if not line:
                continue

            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    return events


def get_request_events(request_id: str):
    """
    Return all audit events belonging to one request.
    """

    events = get_audit_events()

    return [
        event
        for event in events
        if event.get("request_id") == request_id
    ]
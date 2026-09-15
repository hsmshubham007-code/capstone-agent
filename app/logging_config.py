import json
import logging
import sys
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):
    """
    Format application logs as JSON.

    JSON logs are easier for production systems,
    log aggregators, and monitoring platforms to parse.
    """

    def format(self, record):
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Optional structured fields
        for field in [
            "request_id",
            "thread_id",
            "endpoint",
            "tool",
            "latency_ms",
            "status",
            "error",
        ]:
            value = getattr(record, field, None)

            if value is not None:
                log_data[field] = value

        return json.dumps(log_data, default=str)


def setup_logging():
    """
    Configure application-wide structured logging.
    """

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    root_logger = logging.getLogger()

    # Avoid duplicate handlers if setup_logging()
    # is called more than once.
    if not root_logger.handlers:
        root_logger.addHandler(handler)

    root_logger.setLevel(logging.INFO)

    return root_logger
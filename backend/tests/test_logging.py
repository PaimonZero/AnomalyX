import json
import logging
from datetime import datetime, timezone

from app.core.logging import JsonLogFormatter


def test_json_log_formatter_uses_record_created_timestamp() -> None:
    record = logging.LogRecord(
        name="test.logger",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="hello",
        args=(),
        exc_info=None,
    )
    record.created = 1_700_000_000.0

    payload = json.loads(JsonLogFormatter().format(record))

    assert payload["timestamp"] == datetime.fromtimestamp(
        record.created,
        tz=timezone.utc,
    ).isoformat()

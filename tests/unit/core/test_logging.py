import json

import pytest
import structlog

from core.config import Settings
from core.logging import configure_logging


def test_configure_logging_emits_json_in_non_local_environments(
    capsys: pytest.CaptureFixture[str],
) -> None:
    configure_logging(Settings(environment="staging", _env_file=None))

    structlog.get_logger("test").info("hello", foo="bar")

    events = [json.loads(line) for line in capsys.readouterr().err.splitlines()]
    event = next(e for e in events if e["event"] == "hello")
    assert event["foo"] == "bar"

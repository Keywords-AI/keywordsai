import datetime
from unittest.mock import MagicMock

from keywordsai_exporter_braintrust import KeywordsAIExporter


class DummyLazyValue:
    def __init__(self, value):
        self._value = value

    def get(self):
        return self._value


def test_flush_sends_payload_with_trace_fields():
    session = MagicMock()
    session.post.return_value = MagicMock(ok=True, status_code=200, text="ok")

    exporter = KeywordsAIExporter(
        api_key="test-key",
        base_url="https://api.keywordsai.co/api",
        session=session,
    )

    event = {
        "id": "log-1",
        "span_id": "span-456",
        "root_span_id": "trace-123",
        "span_parents": [],
        "span_attributes": {"name": "root", "type": "llm"},
        "input": {"messages": [{"role": "user", "content": "Hi"}]},
        "output": "Hello",
        "metadata": {"request_id": "req-1"},
        "tags": ["tag1"],
        "scores": {"accuracy": 0.9},
        "metrics": {"start": 1700000000.0, "end": 1700000001.5},
    }

    exporter.log(DummyLazyValue(event))
    exporter.flush()

    assert session.post.call_count == 1
    _, kwargs = session.post.call_args
    payload = kwargs["json"]

    expected_start = datetime.datetime.fromtimestamp(1700000000.0, tz=datetime.timezone.utc).isoformat()
    expected_end = datetime.datetime.fromtimestamp(1700000001.5, tz=datetime.timezone.utc).isoformat()

    assert payload["trace_unique_id"] == "trace-123"
    assert payload["span_unique_id"] == "span-456"
    assert payload["span_parent_id"] is None
    assert payload["trace_name"] == "root"
    assert payload["span_name"] == "root"
    assert payload["log_type"] == "generation"
    assert payload["latency"] == 1.5
    assert payload["start_time"] == expected_start
    assert payload["timestamp"] == expected_end

    metadata = payload["metadata"]
    assert metadata["braintrust_tags"] == ["tag1"]
    assert metadata["braintrust_scores"] == {"accuracy": 0.9}


def test_child_span_sets_parent_id_and_no_trace_name():
    session = MagicMock()
    session.post.return_value = MagicMock(ok=True, status_code=200, text="ok")

    exporter = KeywordsAIExporter(
        api_key="test-key",
        base_url="https://api.keywordsai.co/api",
        session=session,
    )

    event = {
        "id": "log-2",
        "span_id": "span-child",
        "root_span_id": "trace-parent",
        "span_parents": ["span-parent"],
        "span_attributes": {"name": "child", "type": "task"},
        "metrics": {"start": 1700000002.0, "end": 1700000004.0},
    }

    exporter.log(DummyLazyValue(event))
    exporter.flush()

    _, kwargs = session.post.call_args
    payload = kwargs["json"]

    assert payload["span_parent_id"] == "span-parent"
    assert payload["trace_name"] is None
    assert payload["log_type"] == "task"

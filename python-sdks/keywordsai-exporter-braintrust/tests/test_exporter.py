from unittest.mock import MagicMock

import braintrust

from keywordsai_exporter_braintrust import KeywordsAIExporter


def _init_test_logger():
    return braintrust.init_logger(
        project="Test Project",
        project_id="test-project-id",
        api_key=braintrust.logger.TEST_API_KEY,
        async_flush=False,
        set_current=False,
    )


def _build_exporter(session):
    return KeywordsAIExporter(
        api_key="test-key",
        base_url="https://api.keywordsai.co/api",
        session=session,
    )


def test_braintrust_root_span_sends_payload_with_trace_fields():
    session = MagicMock()
    session.post.return_value = MagicMock(ok=True, status_code=200, text="ok")

    exporter = _build_exporter(session)
    with exporter:
        logger = _init_test_logger()
        with logger.start_span(name="root", type="llm") as span:
            span.log(
                input=[{"role": "user", "content": "Hi"}],
                output="Hello",
                metadata={"request_id": "req-1"},
                tags=["tag1"],
                scores={"accuracy": 0.9},
            )
        logger.flush()

    assert session.post.call_count == 1
    args, kwargs = session.post.call_args
    assert args[0] == "https://api.keywordsai.co/api/v1/traces/ingest"
    payloads = kwargs["json"]
    assert isinstance(payloads, list)
    assert len(payloads) == 1
    payload = payloads[0]

    assert payload["trace_unique_id"] == payload["span_unique_id"]
    assert payload["span_parent_id"] is None
    assert payload["trace_name"] == "root"
    assert payload["span_name"] == "root"
    assert payload["log_type"] == "generation"

    metadata = payload["metadata"]
    assert metadata["braintrust_tags"] == ["tag1"]
    assert metadata["braintrust_scores"] == {"accuracy": 0.9}


def test_braintrust_child_span_sets_parent_id_and_no_trace_name():
    session = MagicMock()
    session.post.return_value = MagicMock(ok=True, status_code=200, text="ok")

    exporter = _build_exporter(session)
    with exporter:
        logger = _init_test_logger()
        with logger.start_span(name="root", type="task") as root_span:
            with root_span.start_span(name="child", type="task") as child_span:
                child_span.log(metadata={"child": True})
        logger.flush()

    args, kwargs = session.post.call_args
    assert args[0] == "https://api.keywordsai.co/api/v1/traces/ingest"
    payloads = kwargs["json"]
    assert isinstance(payloads, list)
    assert len(payloads) >= 2

    child_payloads = [payload for payload in payloads if payload.get("span_parent_id")]
    assert len(child_payloads) == 1
    child_payload = child_payloads[0]

    assert child_payload["trace_name"] is None
    assert child_payload["log_type"] == "task"

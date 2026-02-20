import os
import time
from unittest.mock import MagicMock

import braintrust
import pytest

from respan_exporter_braintrust import RespanBraintrustExporter


def _init_test_logger():
    return braintrust.init_logger(
        project="Test Project",
        project_id="test-project-id",
        api_key=braintrust.logger.TEST_API_KEY,
        async_flush=False,
        set_current=False,
    )


def _build_exporter(session):
    return RespanBraintrustExporter(
        api_key="test-key",
        base_url="https://api.respan.ai/api",
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
                metadata={"request_id": "req-1", "model": "gpt-4o-mini"},
                tags=["tag1"],
                scores={"accuracy": 0.9},
                metrics={"prompt_tokens": 12, "completion_tokens": 34},
            )
        logger.flush()

    assert session.post.call_count == 1
    args, kwargs = session.post.call_args
    assert args[0] == "https://api.respan.ai/api/v1/traces/ingest"
    payloads = kwargs["json"]
    assert isinstance(payloads, list)
    assert len(payloads) == 1
    payload = payloads[0]

    assert payload["trace_unique_id"] == payload["span_unique_id"]
    assert "-" not in payload["trace_unique_id"]
    assert len(payload["trace_unique_id"]) == 32
    assert "-" not in payload["span_unique_id"]
    assert len(payload["span_unique_id"]) == 32
    assert payload["span_parent_id"] is None
    assert payload["trace_name"] == "root"
    assert payload["span_name"] == "root"
    assert payload["log_type"] == "generation"
    assert payload["model"] == "gpt-4o-mini"
    assert payload["prompt_tokens"] == 12
    assert payload["completion_tokens"] == 34
    assert payload["total_request_tokens"] == 46

    metadata = payload["metadata"]
    assert metadata["braintrust_tags"] == "[\"tag1\"]"
    assert metadata["braintrust_scores"] == "{\"accuracy\": 0.9}"
    assert "-" not in metadata["braintrust_log_id"]
    assert len(metadata["braintrust_log_id"]) == 32


def test_braintrust_child_span_sets_parent_id_and_no_trace_name():
    session = MagicMock()
    session.post.return_value = MagicMock(ok=True, status_code=200, text="ok")

    exporter = _build_exporter(session)
    with exporter:
        logger = _init_test_logger()
        with logger.start_span(name="root", type="task") as root_span:
            with root_span.start_span(name="child", type="chat") as child_span:
                child_span.log(metadata={"child": True})
        logger.flush()

    args, kwargs = session.post.call_args
    assert args[0] == "https://api.respan.ai/api/v1/traces/ingest"
    payloads = kwargs["json"]
    assert isinstance(payloads, list)
    assert len(payloads) >= 2

    child_payloads = [payload for payload in payloads if payload.get("span_parent_id")]
    assert len(child_payloads) == 1
    child_payload = child_payloads[0]

    assert child_payload["trace_name"] is None
    assert child_payload["log_type"] == "chat"
    assert "-" not in child_payload["span_parent_id"]
    assert len(child_payload["span_parent_id"]) == 32


def test_braintrust_real_send_smoke():
    api_key = os.getenv("RESPAN_API_KEY")
    if not api_key:
        pytest.skip("RESPAN_API_KEY not set")

    exporter = RespanBraintrustExporter(api_key=api_key, raise_on_error=True)
    with exporter:
        logger = _init_test_logger()
        with logger.start_span(name="braintrust-send-test-parent", type="task") as root_span:
            with root_span.start_span(name="braintrust-send-test-child", type="chat") as child_span:
                time.sleep(1.2)
                child_span.log(
                    input=[{"role": "user", "content": "Hello from braintrust logger"}],
                    output="Hello for response",
                    metrics={"prompt_tokens": 5, "completion_tokens": 7},
                    metadata={"model": "gpt-4o-mini"},
                )
        logger.flush()

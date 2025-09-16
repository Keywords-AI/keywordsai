import os
import json
from typing import Any, Dict, List

import pytest

from opentelemetry.sdk.trace import ReadableSpan
from keywordsai_tracing import KeywordsAITelemetry, workflow, task


HAS_KEY = bool(os.getenv("OPENAI_API_KEY"))


def _serialize(span: ReadableSpan) -> Dict[str, Any]:
    attrs = getattr(span, "attributes", {}) or {}
    status = getattr(getattr(span, "status", None), "status_code", None)
    try:
        status_str = getattr(status, "name", None) or str(status)
    except Exception:
        status_str = None
    return {
        "name": getattr(span, "name", ""),
        "kind": attrs.get("traceloop.span.kind"),
        "entityPath": attrs.get("traceloop.entity.path"),
        "entityName": attrs.get("traceloop.entity.name"),
        "aiModel": attrs.get("gen_ai.model.id"),
        "aiSystem": attrs.get("gen_ai.system"),
        "status": status_str,
    }


def _init_telemetry(collected: List[Dict[str, Any]]):
    def cb(span: ReadableSpan):
        data = _serialize(span)
        collected.append(data)
        print("[Span]", json.dumps(data, sort_keys=True))

    KeywordsAITelemetry(
        app_name="test-openai-responses-live",
        span_postprocess_callback=cb,
        disable_batch=True,
        enabled=True,
    )


def _get_openai_client():
    import openai
    return openai.Client()


@workflow(name="responses_live")
def _responses_live_flow() -> Dict[str, Any]:
    @task(name="responses_live_task")
    def inner() -> Dict[str, Any]:
        client = _get_openai_client()
        created = client.responses.create(
            model="gpt-4o-mini",
            input=[{"role": "user", "content": [{"type": "text", "text": "hi"}]}],
        )
        retrieved = client.responses.retrieve(created.id)
        return {"created": created.id, "retrieved": getattr(retrieved, "id", None)}

    return inner()


@pytest.mark.skipif(not HAS_KEY, reason="OPENAI_API_KEY not set")
def test_openai_responses_live_traced():
    collected: List[Dict[str, Any]] = []
    _init_telemetry(collected)
    out = _responses_live_flow()
    assert out.get("created")
    assert out.get("retrieved") == out.get("created")
    # Expect workflow/task; check for any openai/gen_ai span
    assert any(s.get("kind") for s in collected)
    maybe_openai = [s for s in collected if (s.get("aiSystem") == "openai" or "responses" in (s.get("name") or "").lower())]
    print("[OpenAI-like spans]", json.dumps(maybe_openai, indent=2))

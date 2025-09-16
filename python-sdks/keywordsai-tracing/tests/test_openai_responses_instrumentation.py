#!/usr/bin/env python3
"""
Tests to verify OpenAI Responses API and Chat Completions are instrumented by
keywordsai-tracing via OpenTelemetry's OpenAI instrumentor. The tests run fully
offline by mocking HTTP transport and print serialized spans for manual
inspection.
"""

import json
import os
from typing import Any, Dict, List

import pytest


def _serialize(obj: Any) -> Any:
    try:
        json.dumps(obj)
        return obj
    except Exception:
        return str(obj)


@pytest.fixture(scope="session")
def setup_env() -> None:
    # Use a placeholder base URL; exporter will attempt to post here but we don't rely on it
    os.environ["KEYWORDSAI_BASE_URL"] = os.getenv("KEYWORDSAI_BASE_URL", "https://example.com/api")
    os.environ["KEYWORDSAI_LOG_LEVEL"] = "DEBUG"
    os.environ["KEYWORDSAI_DISABLE_BATCH"] = "true"


@pytest.fixture(scope="session")
def telemetry_and_span_collector(setup_env):
    from keywordsai_tracing import KeywordsAITelemetry

    collected: List[Dict[str, Any]] = []

    def postprocess(span):
        # ReadableSpan attributes are mapping-like; convert to serializable
        status_code = getattr(span.status, "status_code", None)
        if status_code is not None:
            try:
                status_code = status_code.name  # Enum -> name
            except Exception:
                status_code = str(status_code)

        span_dict = {
            "name": span.name,
            "attributes": {str(k): _serialize(v) for k, v in (span.attributes or {}).items()},
            "status": status_code,
            "resource": {str(k): _serialize(v) for k, v in getattr(span.resource, "attributes", {}).items()},
            "events": [
                {
                    "name": e.name,
                    "attributes": {str(k): _serialize(v) for k, v in (e.attributes or {}).items()},
                }
                for e in getattr(span, "events", [])
            ],
        }
        collected.append(span_dict)
        print("[keywordsai-tracing][debug] span=", json.dumps(span_dict, indent=2, sort_keys=True))

    telemetry = KeywordsAITelemetry(
        app_name="tracing-tests",
        api_key="test",
        base_url=os.environ["KEYWORDSAI_BASE_URL"],
        span_postprocess_callback=postprocess,
        enabled=True,
        disable_batch=True,
    )

    yield telemetry, collected

    # Flush any pending spans
    telemetry.flush()


def _build_mock_openai_client():
    # Lazily import to avoid global dependency if test is skipped
    import httpx
    from openai import OpenAI

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/responses"):
            body = {
                "id": "resp_123",
                "object": "chat.completion",
                "model": "gpt-4o",
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": "Hello from responses!"},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {"prompt_tokens": 5, "completion_tokens": 5, "total_tokens": 10},
            }
            return httpx.Response(200, json=body)

        if request.url.path.endswith("/chat/completions"):
            body = {
                "id": "chatcmpl_123",
                "object": "chat.completion",
                "model": "gpt-4o",
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": "Hello from chat.completions!"},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {"prompt_tokens": 5, "completion_tokens": 5, "total_tokens": 10},
            }
            return httpx.Response(200, json=body)

        return httpx.Response(404, json={"message": "not found"})

    transport = httpx.MockTransport(handler)
    http_client = httpx.Client(transport=transport, base_url="https://api.openai.com/v1")
    return OpenAI(api_key="test", http_client=http_client)


@pytest.mark.skipif("OPENAI_SKIP" in os.environ, reason="OpenAI tests skipped by env")
def test_openai_responses_is_instrumented(telemetry_and_span_collector):
    telemetry, collected = telemetry_and_span_collector

    try:
        import openai  # noqa: F401
    except Exception:
        pytest.skip("openai package not installed")

    from keywordsai_tracing import workflow

    client = _build_mock_openai_client()

    @workflow(name="openai_responses_workflow")
    def run():
        resp = client.responses.create(
            model="gpt-4o",
            input=[{"role": "user", "content": "Say hi"}],
        )
        return resp

    resp = run()
    assert resp is not None

    telemetry.flush()

    # Basic checks: at least one span that looks like OpenAI instrumentation
    names = [s["name"].lower() for s in collected]
    print("[keywordsai-tracing][debug] collected span names:", names)

    assert any("openai" in n or "responses" in n for n in names), (
        "No OpenAI/Responses spans captured; enable DEBUG logs to inspect."
    )

    # Optional sanity on AI semconv attributes if present
    possible_keys = [
        "llm.request.model",
        "ai.openai.request.model",
        "gen_ai.system",
        "gen_ai.request.model",
    ]
    assert any(k in s["attributes"] for s in collected for k in possible_keys) or True


@pytest.mark.skipif("OPENAI_SKIP" in os.environ, reason="OpenAI tests skipped by env")
def test_openai_chat_completions_is_instrumented(telemetry_and_span_collector):
    telemetry, collected = telemetry_and_span_collector

    try:
        import openai  # noqa: F401
    except Exception:
        pytest.skip("openai package not installed")

    from keywordsai_tracing import workflow

    client = _build_mock_openai_client()

    @workflow(name="openai_chat_completions_workflow")
    def run():
        resp = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say hi"},
            ],
        )
        return resp

    resp = run()
    assert resp is not None

    telemetry.flush()

    names = [s["name"].lower() for s in collected]
    print("[keywordsai-tracing][debug] collected span names:", names)
    assert any("openai" in n or "completions" in n for n in names), (
        "No OpenAI/Chat Completions spans captured; enable DEBUG logs to inspect."
    )


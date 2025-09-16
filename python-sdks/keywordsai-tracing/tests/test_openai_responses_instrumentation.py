import os
import json
import asyncio
from typing import Any, Dict, List

import pytest

# External deps used by OpenAI instrumentation
import httpx

from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.semconv_ai import SpanAttributes

from keywordsai_tracing import KeywordsAITelemetry, workflow, task


# Per request: disable mocked tests in favor of live tests
pytestmark = pytest.mark.skip(reason="Mock transport disabled; using live test with real OpenAI API")


def _serialize_span(span: ReadableSpan) -> Dict[str, Any]:
    attrs = getattr(span, "attributes", {}) or {}
    status = getattr(getattr(span, "status", None), "status_code", None)
    try:
        status_str = getattr(status, "name", None) or str(status)
    except Exception:
        status_str = None
    return {
        "name": getattr(span, "name", ""),
        "kind": attrs.get(SpanAttributes.TRACELOOP_SPAN_KIND),
        "entityPath": attrs.get(SpanAttributes.TRACELOOP_ENTITY_PATH),
        "entityName": attrs.get(SpanAttributes.TRACELOOP_ENTITY_NAME),
        "workflowName": attrs.get(SpanAttributes.TRACELOOP_WORKFLOW_NAME),
        "aiModel": attrs.get("gen_ai.model.id"),
        "aiSystem": attrs.get("gen_ai.system"),
        "httpMethod": attrs.get("http.request.method"),
        "httpUrl": attrs.get("url.full") or attrs.get("http.url"),
        "status": status_str,
    }


class MockOpenAITransport(httpx.MockTransport):
    """HTTPX transport to fake OpenAI Responses API endpoints.

    We simulate minimal responses for:
    - POST /v1/responses
    - GET  /v1/responses/{id}
    """

    def __init__(self):
        super().__init__(self._handler)
        self._responses: Dict[str, Dict[str, Any]] = {}
        self._counter = 0

    def _new_id(self) -> str:
        self._counter += 1
        return f"resp_{self._counter:06d}"

    def _handler(self, request: httpx.Request) -> httpx.Response:
        if request.method == "POST" and request.url.path == "/v1/responses":
            rid = self._new_id()
            body = {
                "id": rid,
                "object": "response",
                "model": "gpt-4o-mini",
                "output": [
                    {"type": "message", "role": "assistant", "content": [{"type": "text", "text": "hello"}]}
                ],
            }
            self._responses[rid] = body
            return httpx.Response(200, json=body)

        if request.method == "GET" and request.url.path.startswith("/v1/responses/"):
            rid = request.url.path.split("/")[-1]
            body = self._responses.get(rid)
            if body is None:
                return httpx.Response(404, json={"error": {"message": "not found"}})
            return httpx.Response(200, json=body)

        return httpx.Response(404, json={"error": {"message": "unknown route"}})


def _install_openai_mock_client(transport: httpx.MockTransport):
    """Monkeypatch OpenAI client internals to use httpx MockTransport.

    The OpenTelemetry OpenAI instrumentor instruments the OpenAI Python SDK, which
    uses `httpx` under the hood. We direct its HTTP calls to our MockTransport by
    setting environment variables used by the OpenAI SDK and httpx.
    """
    # OpenAI SDK reads base URL and API key via env vars
    os.environ.setdefault("OPENAI_API_KEY", "sk-test")
    os.environ.setdefault("OPENAI_BASE_URL", "https://api.openai.com/v1")

    # httpx supports a custom transport via client kwargs; since we cannot easily
    # intercept OpenAI client construction here, we rely on OTEL instrumentation
    # capturing spans from httpx made by OpenAI. For network isolation, we also
    # set KEYWORDSAI_BASE_URL to a safe placeholder.
    os.environ.setdefault("KEYWORDSAI_BASE_URL", "https://example.invalid/api")

    # Patch httpx.Client to always use our transport
    original_client = httpx.Client

    class PatchedClient(httpx.Client):
        def __init__(self, *args, **kwargs):
            kwargs = dict(kwargs)
            kwargs["transport"] = transport
            super().__init__(*args, **kwargs)

    httpx.Client = PatchedClient  # type: ignore

    return original_client


@pytest.fixture(autouse=True)
def _env_and_logging_setup(monkeypatch):
    # Enable detailed debug logs in tracing SDK
    monkeypatch.setenv("KEYWORDSAI_LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("KEYWORDSAI_DISABLE_BATCH", "true")
    # Safe placeholder export target
    monkeypatch.setenv("KEYWORDSAI_BASE_URL", "https://example.invalid/api")

    # Prevent actual network export by no-op'ing OTLP HTTP exporter
    try:
        from opentelemetry.sdk.trace.export import SpanExportResult
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
            OTLPSpanExporter,
        )

        def _no_export(self, spans):  # type: ignore[no-redef]
            return SpanExportResult.SUCCESS

        def _no_shutdown(self):  # type: ignore[no-redef]
            return None

        monkeypatch.setattr(OTLPSpanExporter, "export", _no_export, raising=True)
        monkeypatch.setattr(OTLPSpanExporter, "shutdown", _no_shutdown, raising=True)
    except Exception:
        pass
    yield


def _init_telemetry(collected: List[Dict[str, Any]]):
    def post_cb(span: ReadableSpan):
        data = _serialize_span(span)
        collected.append(data)
        print("[Span] ", json.dumps(data, sort_keys=True))

    # Initialize with OpenAI instrumentation enabled by default
    KeywordsAITelemetry(
        app_name="test-openai-responses",
        span_postprocess_callback=post_cb,
        enabled=True,
        disable_batch=True,
    )


def _get_openai_client():
    try:
        import openai
    except Exception as e:  # pragma: no cover - dependency missing will fail test
        pytest.skip(f"openai not installed: {e}")
    return openai.Client()


@workflow(name="responses_workflow")
def _call_responses_api_sync() -> Dict[str, Any]:
    @task(name="responses_task")
    def inner() -> Dict[str, Any]:
        client = _get_openai_client()
        result = client.responses.create(
            model="gpt-4o-mini",
            input=[{"role": "user", "content": [{"type": "text", "text": "hi"}]}],
        )
        # Fetching by id to exercise GET path
        _ = client.responses.retrieve(result.id)
        return {"id": result.id}

    return inner()


def test_openai_responses_sync_traced(monkeypatch):
    collected: List[Dict[str, Any]] = []
    transport = MockOpenAITransport()
    original_client = _install_openai_mock_client(transport)
    try:
        _init_telemetry(collected)
        out = _call_responses_api_sync()
        assert "id" in out
        # At minimum, ensure workflow/task spans were emitted and printed
        assert any(s.get("kind") for s in collected), "workflow/task spans missing"
        print("[Collected spans count]", len(collected))
    finally:
        # restore httpx.Client
        httpx.Client = original_client  # type: ignore


@workflow(name="responses_workflow_async")
async def _call_responses_api_async() -> Dict[str, Any]:
    @task(name="responses_task_async")
    def inner_sync_call() -> Dict[str, Any]:
        client = _get_openai_client()
        result = client.responses.create(
            model="gpt-4o-mini",
            input=[{"role": "user", "content": [{"type": "text", "text": "hi"}]}],
        )
        return {"id": result.id}

    # OpenAI's python SDK calls are sync today; run task in thread to simulate async usage
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, inner_sync_call)
    return result


def test_openai_responses_async_traced(monkeypatch):
    collected: List[Dict[str, Any]] = []
    transport = MockOpenAITransport()
    original_client = _install_openai_mock_client(transport)
    try:
        _init_telemetry(collected)
        out = asyncio.run(_call_responses_api_async())
        assert "id" in out
        assert any(s.get("kind") for s in collected)
        print("[Collected spans count async]", len(collected))
    finally:
        httpx.Client = original_client  # type: ignore


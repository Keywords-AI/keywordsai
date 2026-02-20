"""Basic Agno tracing test for Keywords AI exporter."""

import os

import pytest

pytest.importorskip("agno")
pytest.importorskip("openai")
pytest.importorskip("openinference.instrumentation.agno")
pytest.importorskip("opentelemetry.sdk")

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from openinference.instrumentation.agno import AgnoInstrumentor
from opentelemetry import trace as trace_api
from opentelemetry.sdk import trace as trace_sdk
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

from respan_exporter_agno import RespanAgnoInstrumentor


def test_agno_tracing_exporter_basic():
    """Run an Agno agent and send traces to Respan."""

    respan_api_key = os.getenv("RESPAN_API_KEY")
    if not respan_api_key:
        pytest.skip("RESPAN_API_KEY not set")

    def _gateway_base_url() -> str:
        base_url = (
            os.getenv("RESPAN_GATEWAY_BASE_URL")
            or os.getenv("RESPAN_BASE_URL")
            or "https://api.respan.ai"
        )
        base = base_url.rstrip("/")
        for suffix in ("/v1/traces/ingest", "/v1/traces", "/v1"):
            if base.endswith(suffix):
                base = base[: -len(suffix)]
                break
        if not base.endswith("/api"):
            base = f"{base}/api"
        return base

    tracer_provider = trace_api.get_tracer_provider()
    if not isinstance(tracer_provider, trace_sdk.TracerProvider):
        tracer_provider = trace_sdk.TracerProvider()
        trace_api.set_tracer_provider(tracer_provider)

    tracer_provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))

    RespanAgnoInstrumentor().instrument(
        api_key=respan_api_key,
        endpoint=os.getenv("RESPAN_ENDPOINT"),
        base_url=os.getenv("RESPAN_BASE_URL"),
        passthrough=False,
    )
    AgnoInstrumentor().instrument()

    model_id = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    agent = Agent(
        name="Test Agent",
        model=OpenAIChat(
            id=model_id,
            api_key=respan_api_key,
            base_url=_gateway_base_url(),
        ),
    )
    result = agent.run("hello from Respan Agno exporter test")

    tracer_provider.force_flush()

    assert result is not None

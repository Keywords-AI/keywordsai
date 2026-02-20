"""Tracing endpoint constants for Respan SDK."""

from typing import Optional


RESPAN_TRACING_INGEST_ENDPOINT = "https://api.respan.ai/api/v1/traces/ingest"

# Anti-recursion header: SDK exporter sends this on every export request.
# Server-side tracing decorators MUST check for this header and skip
# EMITTING NEW TRACES for the ingest request — but still PROCESS the
# payload (store the trace in CH). The goal is to prevent infinite loops
# when the ingest endpoint is itself observed, not to drop trace data.
RESPAN_DOGFOOD_HEADER = "X-Respan-Dogfood"


def resolve_tracing_ingest_endpoint(base_url: Optional[str] = None) -> str:
    """Build tracing ingest endpoint from an optional base URL."""
    if not base_url:
        return RESPAN_TRACING_INGEST_ENDPOINT

    normalized_base_url = base_url.rstrip("/")
    if normalized_base_url.endswith("/api"):
        return f"{normalized_base_url}/v1/traces/ingest"

    return f"{normalized_base_url}/api/v1/traces/ingest"

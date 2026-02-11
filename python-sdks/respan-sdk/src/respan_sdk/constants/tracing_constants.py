"""Tracing endpoint constants for Respan SDK."""

from typing import Optional


RESPAN_TRACING_INGEST_ENDPOINT = "https://api.respan.ai/api/v1/traces/ingest"


def resolve_tracing_ingest_endpoint(base_url: Optional[str] = None) -> str:
    """Build tracing ingest endpoint from an optional base URL."""
    if not base_url:
        return RESPAN_TRACING_INGEST_ENDPOINT

    normalized_base_url = base_url.rstrip("/")
    if normalized_base_url.endswith("/api"):
        return f"{normalized_base_url}/v1/traces/ingest"

    return f"{normalized_base_url}/api/v1/traces/ingest"

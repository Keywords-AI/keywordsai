"""API-related constants for Respan SDK.

These constants are shared across all Respan exporters and integrations.
"""

# Base API URLs
DEFAULT_RESPAN_API_BASE_URL = "https://api.respan.ai/api"

# API Paths
TRACES_INGEST_PATH = "v1/traces/ingest"

# Full endpoint URLs (convenience)
DEFAULT_TRACES_INGEST_ENDPOINT = f"{DEFAULT_RESPAN_API_BASE_URL}/{TRACES_INGEST_PATH}"

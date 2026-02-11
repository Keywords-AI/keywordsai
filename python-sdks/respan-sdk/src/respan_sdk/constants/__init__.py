from respan_sdk.constants.tracing_constants import (
    RESPAN_TRACING_INGEST_ENDPOINT,
    resolve_tracing_ingest_endpoint,
)

DEFAULT_EVAL_LLM_ENGINE = "gpt-4o-mini"
EVAL_COST_FALLBACK = 0.001
LLM_ENGINE_FIELD_NAME = "llm_engine"

# Import constants for default values
UTC_EPOCH = "1970-01-01 00:00:00"

__all__ = [
    "DEFAULT_EVAL_LLM_ENGINE",
    "EVAL_COST_FALLBACK",
    "LLM_ENGINE_FIELD_NAME",
    "UTC_EPOCH",
    "RESPAN_TRACING_INGEST_ENDPOINT",
    "resolve_tracing_ingest_endpoint",
]

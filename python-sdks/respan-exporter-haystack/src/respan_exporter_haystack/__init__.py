"""Respan integration for Haystack pipelines."""

from respan_exporter_haystack.connector import RespanConnector
from respan_exporter_haystack.tracer import RespanTracer
from respan_exporter_haystack.gateway import RespanGenerator, RespanChatGenerator

__version__ = "1.0.0"
__all__ = [
    # Tracing (track workflow spans)
    "RespanConnector",
    "RespanTracer",
    # Gateway (route LLM calls through Respan)
    "RespanGenerator",
    "RespanChatGenerator",
]

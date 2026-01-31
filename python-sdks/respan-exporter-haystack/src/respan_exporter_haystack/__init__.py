"""Keywords AI integration for Haystack pipelines."""

from .connector import RespanConnector
from .tracer import RespanTracer
from .gateway import RespanGenerator, RespanChatGenerator

__version__ = "0.1.0"
__all__ = [
    # Tracing (track workflow spans)
    "RespanConnector",
    "RespanTracer",
    # Gateway (route LLM calls through Keywords AI)
    "RespanGenerator",
    "RespanChatGenerator",
]

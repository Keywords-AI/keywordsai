"""Keywords AI integration for Haystack pipelines."""

from .connector import KeywordsAIConnector
from .tracer import KeywordsAITracer
from .gateway import KeywordsAIGenerator, KeywordsAIChatGenerator

__version__ = "0.1.0"
__all__ = [
    # Tracing (track workflow spans)
    "KeywordsAIConnector",
    "KeywordsAITracer",
    # Gateway (route LLM calls through Keywords AI)
    "KeywordsAIGenerator",
    "KeywordsAIChatGenerator",
]

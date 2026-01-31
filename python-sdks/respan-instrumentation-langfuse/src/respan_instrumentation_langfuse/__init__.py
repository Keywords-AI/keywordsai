"""Keywords AI Instrumentation for Langfuse.

This package provides OTEL-compliant automatic instrumentation for Langfuse 
to send traces to Keywords AI.

Usage:
    # IMPORTANT: Instrument BEFORE importing Langfuse
    from respan_instrumentation_langfuse import LangfuseInstrumentor
    
    LangfuseInstrumentor().instrument(api_key="your-api-key")
    
    # Now use Langfuse normally
    from langfuse import Langfuse, observe
    
    @observe()
    def my_function():
        return "Traced to Keywords AI!"

Auto-instrumentation:
    Set RESPAN_API_KEY environment variable, then:
    
        opentelemetry-instrument python your_app.py
"""

__version__ = "0.2.0"

import logging
import os

logger = logging.getLogger(__name__)

# Import the instrumentor
from .instrumentor import LangfuseInstrumentor

__all__ = ["LangfuseInstrumentor"]

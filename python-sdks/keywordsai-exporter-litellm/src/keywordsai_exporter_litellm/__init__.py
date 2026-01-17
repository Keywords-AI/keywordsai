"""Keywords AI Exporter for LiteLLM.

This package provides OpenTelemetry-compliant instrumentation for LiteLLM
that exports traces to the Keywords AI platform.

Two approaches are provided:

1. LiteLLMInstrumentor (recommended) - OTEL-compliant instrumentor using wrapt patching:

    from keywordsai_exporter_litellm import LiteLLMInstrumentor
    
    LiteLLMInstrumentor().instrument(api_key="your-api-key")
    
    import litellm
    response = litellm.completion(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Hello!"}]
    )

2. KeywordsAILiteLLMCallback - LiteLLM-native callback:

    import litellm
    from keywordsai_exporter_litellm import KeywordsAILiteLLMCallback
    
    callback = KeywordsAILiteLLMCallback(api_key="your-api-key")
    # Pass the bound methods to success_callback and failure_callback
    litellm.success_callback = [callback.log_success_event]
    litellm.failure_callback = [callback.log_failure_event]
    
    response = litellm.completion(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Hello!"}]
    )
"""

from .exporter import (
    KeywordsAILiteLLMCallback,
    KeywordsAILogger,
    KeywordsAISpanExporter,
    LiteLLMInstrumentor,
)

__all__ = [
    "LiteLLMInstrumentor",
    "KeywordsAILiteLLMCallback",
    "KeywordsAISpanExporter",
    "KeywordsAILogger",  # Legacy, for backwards compatibility
]

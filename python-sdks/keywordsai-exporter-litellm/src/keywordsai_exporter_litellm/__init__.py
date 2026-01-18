"""Keywords AI Exporter for LiteLLM.

This package provides a callback integration for LiteLLM
that exports traces to the Keywords AI platform.

Usage:

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
)

__all__ = [
    "KeywordsAILiteLLMCallback",
    "KeywordsAILogger",  # Legacy, for backwards compatibility
]

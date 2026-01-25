"""Keywords AI Exporter for LiteLLM.

This package provides a callback integration for LiteLLM
that exports traces to the Keywords AI platform.

Usage:
    import litellm
    from keywordsai_exporter_litellm import KeywordsAILiteLLMCallback
    
    callback = KeywordsAILiteLLMCallback(api_key="your-api-key")
    litellm.success_callback = [callback.log_success_event]
    litellm.failure_callback = [callback.log_failure_event]
    
    response = litellm.completion(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Hello!"}]
    )
"""

from .exporter import KeywordsAILiteLLMCallback

__all__ = ["KeywordsAILiteLLMCallback"]

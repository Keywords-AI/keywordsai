"""Keywords AI Exporter for LiteLLM.

This package provides a callback integration for LiteLLM
that exports traces to the Keywords AI platform.

Usage:
    import litellm
    from respan_exporter_litellm import RespanLiteLLMCallback
    
    callback = RespanLiteLLMCallback(api_key="your-api-key")
    litellm.success_callback = [callback.log_success_event]
    litellm.failure_callback = [callback.log_failure_event]
    
    response = litellm.completion(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Hello!"}]
    )
"""

from .exporter import RespanLiteLLMCallback

__all__ = ["RespanLiteLLMCallback"]

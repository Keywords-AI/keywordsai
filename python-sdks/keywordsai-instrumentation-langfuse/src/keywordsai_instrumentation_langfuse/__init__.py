"""Keywords AI Instrumentation for Langfuse.

This package provides automatic instrumentation for Langfuse to send traces to Keywords AI.

Usage:
    Instead of:
        from langfuse import Langfuse
    
    Use:
        from keywordsai_instrumentation_langfuse import Langfuse
    
    That's it! All traces will now be sent to Keywords AI automatically.
    Make sure to set KEYWORDSAI_API_KEY in your environment variables.

Example:
    import os
    from keywordsai_instrumentation_langfuse import Langfuse
    
    # Initialize Langfuse as normal
    langfuse = Langfuse(
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
        secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    )
    
    # Use Langfuse decorators as normal - traces will go to Keywords AI
    from keywordsai_instrumentation_langfuse import observe
    
    @observe()
    def my_function():
        return "Hello World"
"""

import os
import logging
from typing import Optional

# Import and apply the patch before importing Langfuse
from .exporter import patch_langfuse_exporter, unpatch_langfuse_exporter, is_patched

# Apply the patch automatically on import
try:
    patch_langfuse_exporter()
except ValueError as e:
    # If no API key is set, warn but don't fail the import
    logging.warning(
        f"Keywords AI instrumentation not activated: {e}. "
        "Langfuse will use its default behavior. "
        "Set KEYWORDSAI_API_KEY to enable Keywords AI tracing."
    )

# Now import and re-export Langfuse components
from langfuse import Langfuse as _LangfuseOriginal
from langfuse.decorators import observe, langfuse_context

# Configure the global langfuse_context to use Keywords AI
keywordsai_base_url = os.getenv("KEYWORDSAI_BASE_URL", "https://api.keywordsai.co/api")
keywordsai_api_key = os.getenv("KEYWORDSAI_API_KEY")
keywordsai_endpoint = "https://api.keywordsai.co/api/v1/traces/ingest"

if keywordsai_api_key:
    from .http_interceptor import KeywordsAIHTTPClient
    
    # Create custom HTTP client that intercepts Langfuse requests
    custom_client = KeywordsAIHTTPClient(
        api_key=keywordsai_api_key,
        endpoint=keywordsai_endpoint
    )
    
    langfuse_context.configure(
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY", ""),
        secret_key=os.getenv("LANGFUSE_SECRET_KEY", ""),
        host="https://api.keywordsai.co",  # Base host without /api path
        httpx_client=custom_client
    )


class Langfuse(_LangfuseOriginal):
    """Wrapper around Langfuse that handles base_url parameter and defaults to Keywords AI."""
    
    def __init__(self, *args, base_url=None, host=None, httpx_client=None, **kwargs):
        """Initialize Langfuse with optional base_url parameter.
        
        Args:
            base_url: Base URL for Langfuse (defaults to KEYWORDSAI_BASE_URL env var)
            host: The Langfuse host URL
            httpx_client: Custom HTTP client
            *args, **kwargs: Other Langfuse parameters
        """
        # If no custom client provided and Keywords AI is configured, use interceptor
        if httpx_client is None and keywordsai_api_key:
            from .http_interceptor import KeywordsAIHTTPClient
            httpx_client = KeywordsAIHTTPClient(
                api_key=keywordsai_api_key,
                endpoint=keywordsai_endpoint
            )
        
        # Set host to Keywords AI base
        if host is None:
            host = base_url if base_url else "https://api.keywordsai.co"
        
        # Pass parameters to the original Langfuse
        kwargs['host'] = host
        if httpx_client:
            kwargs['httpx_client'] = httpx_client
        
        super().__init__(*args, **kwargs)


__version__ = "0.1.0"

__all__ = [
    "Langfuse",
    "observe",
    "langfuse_context",
    "patch_langfuse_exporter",
    "unpatch_langfuse_exporter",
    "is_patched",
]

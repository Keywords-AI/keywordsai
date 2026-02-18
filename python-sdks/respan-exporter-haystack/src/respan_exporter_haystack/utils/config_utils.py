"""Configuration and endpoint helper utilities."""

import os
from typing import Optional

from respan_sdk.constants.api_constants import DEFAULT_RESPAN_API_BASE_URL

DEFAULT_RESPAN_BASE_URL = DEFAULT_RESPAN_API_BASE_URL.removesuffix("/api")


def resolve_api_key(api_key: Optional[str] = None) -> Optional[str]:
    """Resolve API key from explicit value or supported environment variables."""
    if api_key:
        return api_key
    return (
        os.getenv("RESPAN_API_KEY")
        or os.getenv("KEYWORDSAI_API_KEY")
        or os.getenv("KEYWORDS_AI_API_KEY")
    )


def resolve_base_url(base_url: Optional[str] = None, include_api_path: bool = False) -> str:
    """Resolve base URL from explicit value or supported environment variables."""
    if base_url:
        return base_url

    resolved = (
        os.getenv("RESPAN_BASE_URL")
        or os.getenv("KEYWORDSAI_BASE_URL")
        or os.getenv("KEYWORDS_AI_BASE_URL")
    )
    if resolved:
        return resolved

    if include_api_path:
        return DEFAULT_RESPAN_API_BASE_URL
    return DEFAULT_RESPAN_BASE_URL


def build_chat_completions_endpoint(base_url: str) -> str:
    """Build the chat completions endpoint from a Respan base URL."""
    normalized_base_url = base_url.rstrip("/")
    if normalized_base_url.endswith("/api"):
        return f"{normalized_base_url}/chat/completions"
    return f"{normalized_base_url}/api/chat/completions"

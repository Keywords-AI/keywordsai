"""Proxy logging tests for Respan LiteLLM integration."""

import os

import dotenv
import litellm
import pytest

dotenv.load_dotenv(".env", override=True)

# Constants
API_BASE = os.getenv("RESPAN_BASE_URL", "https://api.respan.ai/api")
MODEL = "gpt-4o-mini"


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def _extract_stream_text(chunks):
    """Collect text content from streaming chunks."""
    parts = []
    for chunk in chunks:
        if not chunk:
            continue
        choices = getattr(chunk, "choices", None)
        if choices is None and isinstance(chunk, dict):
            choices = chunk.get("choices")
        if not choices:
            continue
        choice = choices[0]
        delta = getattr(choice, "delta", None)
        if delta is None and isinstance(choice, dict):
            delta = choice.get("delta")
        if delta is not None:
            content = getattr(delta, "content", None)
            if content is None and isinstance(delta, dict):
                content = delta.get("content")
        else:
            message = getattr(choice, "message", None)
            if message is None and isinstance(choice, dict):
                message = choice.get("message")
            content = getattr(message, "content", None)
            if content is None and isinstance(message, dict):
                content = message.get("content")
        if content:
            parts.append(content)
    return "".join(parts)


# -----------------------------------------------------------------------------
# Fixtures
# -----------------------------------------------------------------------------

@pytest.fixture
def api_key():
    """Get API key from environment."""
    key = os.getenv("RESPAN_API_KEY")
    if not key:
        pytest.skip("RESPAN_API_KEY not set")
    return key


# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------

def test_log_with_proxy(api_key):
    """Test single log with proxy mode."""
    response = litellm.completion(
        api_key=api_key,
        api_base=API_BASE,
        model=MODEL,
        messages=[{"role": "user", "content": "Say hello in one word."}],
        extra_body={
            "span_workflow_name": "proxy_logging_non_stream",
            "span_name": "proxy_log_non_stream",
            "customer_identifier": "test_proxy_user_non_stream",
        },
    )
    assert response.choices[0].message.content


def test_log_with_proxy_streaming(api_key):
    """Test single log with proxy streaming mode."""
    response = litellm.completion(
        api_key=api_key,
        api_base=API_BASE,
        model=MODEL,
        stream=True,
        messages=[{"role": "user", "content": "Say hello in one word."}],
        extra_body={
            "span_workflow_name": "proxy_logging_stream",
            "span_name": "proxy_log_stream",
            "customer_identifier": "test_proxy_user_stream",
        },
    )
    chunks = list(response)
    assert len(chunks) > 0
    assert _extract_stream_text(chunks)

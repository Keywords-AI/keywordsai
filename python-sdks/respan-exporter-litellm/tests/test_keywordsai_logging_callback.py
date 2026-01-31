"""Callback logging tests for Keywords AI LiteLLM integration."""

import os

import dotenv
import litellm
import pytest

from keywordsai_exporter_litellm import KeywordsAILiteLLMCallback

dotenv.load_dotenv(".env", override=True)

# Constants
API_BASE = os.getenv("KEYWORDSAI_BASE_URL", "https://api.keywordsai.co/api")
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
    key = os.getenv("KEYWORDSAI_API_KEY")
    if not key:
        pytest.skip("KEYWORDSAI_API_KEY not set")
    return key


@pytest.fixture
def callback(api_key):
    """Setup callback and clean up after test."""
    cb = KeywordsAILiteLLMCallback(api_key=api_key)
    cb.register_litellm_callbacks()

    # Verify callback registration
    success_handler = litellm.success_callback["keywordsai"]
    failure_handler = litellm.failure_callback["keywordsai"]
    assert getattr(success_handler, "__self__", None) is cb
    assert getattr(failure_handler, "__self__", None) is cb

    yield cb

    # Cleanup
    litellm.success_callback = []
    litellm.failure_callback = []


# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------

def test_log_with_callback_non_stream(callback, api_key):
    """Test single log with callback mode (non-stream)."""
    response = litellm.completion(
        api_key=api_key,
        api_base=API_BASE,
        model=MODEL,
        messages=[{"role": "user", "content": "Say hello in one word."}],
        metadata={
            "keywordsai_params": {
                "workflow_name": "callback_logging_non_stream",
                "span_name": "callback_log",
                "customer_identifier": "test_callback_user_non_stream",
            }
        },
    )
    assert response.choices[0].message.content


def test_log_with_callback_streaming(callback, api_key):
    """Test single log with callback streaming mode."""
    response = litellm.completion(
        api_key=api_key,
        api_base=API_BASE,
        model=MODEL,
        stream=True,
        messages=[{"role": "user", "content": "Say hello in one word."}],
        metadata={
            "keywordsai_params": {
                "workflow_name": "callback_logging_stream",
                "span_name": "callback_stream_log",
                "customer_identifier": "test_callback_user_stream",
            }
        },
    )
    chunks = list(response)
    assert len(chunks) > 0
    assert _extract_stream_text(chunks)

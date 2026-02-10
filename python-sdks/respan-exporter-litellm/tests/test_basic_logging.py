"""Basic logging tests for Respan LiteLLM integration."""

import os

import dotenv
import litellm
import pytest

from respan_exporter_litellm import RespanLiteLLMCallback

dotenv.load_dotenv(".env", override=True)

# Constants
API_BASE = os.getenv("RESPAN_BASE_URL", "https://api.respan.ai/api")
MODEL = "gpt-4o-mini"


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


@pytest.fixture
def callback(api_key):
    """Setup callback and clean up after test."""
    cb = RespanLiteLLMCallback(api_key=api_key)
    cb.register_litellm_callbacks()

    # Verify callback registration
    success_handler = litellm.success_callback["respan"]
    failure_handler = litellm.failure_callback["respan"]
    assert getattr(success_handler, "__self__", None) is cb
    assert getattr(failure_handler, "__self__", None) is cb

    yield cb

    # Cleanup
    litellm.success_callback = []
    litellm.failure_callback = []


# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------

def test_log_with_callback_non_stream_basic_logging(callback, api_key):
    """Test single log with callback mode (non-stream)."""
    response = litellm.completion(
        api_key=api_key,
        api_base=API_BASE,
        model=MODEL,
        messages=[{"role": "user", "content": "Say hello in one word."}],
        metadata={
            "respan_params": {
                "workflow_name": "callback_logging_basic_logging",
                "span_name": "callback_log_basic_logging",
                "customer_identifier": "test_callback_user_basic_logging",
            }
        },
    )
    assert response.choices[0].message.content

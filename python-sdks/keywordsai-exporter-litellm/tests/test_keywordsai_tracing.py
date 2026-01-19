"""Test tracing functionality for Keywords AI LiteLLM integration."""
import os
import time
import uuid
from datetime import datetime, timezone

import dotenv
dotenv.load_dotenv(".env", override=True)

import litellm
import pytest

from keywordsai_exporter_litellm import KeywordsAILiteLLMCallback

API_BASE = os.getenv("KEYWORDSAI_BASE_URL")
MODEL = "gpt-4o-mini"


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
    litellm.success_callback = [cb.log_success_event]
    litellm.failure_callback = [cb.log_failure_event]
    yield cb
    litellm.success_callback = []
    litellm.failure_callback = []


def test_trace_with_callback(callback, api_key):
    """Test trace with callback: workflow -> generation."""
    trace_id = uuid.uuid4().hex
    workflow_id = uuid.uuid4().hex[:16]
    workflow_name = "callback_workflow"
    start = datetime.now(timezone.utc)

    response = litellm.completion(
        model=MODEL,
        messages=[{"role": "user", "content": "Say hello, logging callback mode"}],
        metadata={"keywordsai_params": {
            "trace_id": trace_id,
            "parent_span_id": workflow_id,
            "workflow_name": workflow_name,
            "span_name": "generation",
        }},
    )

    assert response.choices[0].message.content


# def test_trace_with_proxy(callback, api_key):
#     """Test trace with proxy mode: workflow -> generation."""
#     trace_id = uuid.uuid4().hex
#     workflow_id = uuid.uuid4().hex[:16]
#     workflow_name = "proxy_workflow"
#     start = datetime.now(timezone.utc)

#     response = litellm.completion(
#         api_key=api_key,
#         api_base=API_BASE,
#         model=MODEL,
#         messages=[{"role": "user", "content": "Say hello, proxy mode"}],
#         metadata={"keywordsai_params": {
#             "trace_id": trace_id,
#             "parent_span_id": workflow_id,
#             "workflow_name": workflow_name,
#             "span_name": "generation",
#         }},
#         extra_body={"customer_identifier": "test_proxy"},
#     )

#     assert response.choices[0].message.content

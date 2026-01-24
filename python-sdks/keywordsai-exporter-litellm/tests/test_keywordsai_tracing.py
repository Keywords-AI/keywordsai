"""Test tracing functionality for Keywords AI LiteLLM integration."""

import os
import uuid

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

def test_trace_with_callback(callback, api_key):
    """Test trace with callback mode: root span -> child span.
    
    Uses KeywordsAI gateway for LLM calls + callback for trace logging.
    Trace structure:
        callback_workflow (trace)
        └── callback_root_generation (root span)
            └── callback_child_generation (child span)
    """
    trace_id = uuid.uuid4().hex
    root_span_id = uuid.uuid4().hex[:16]
    child_span_id = uuid.uuid4().hex[:16]
    workflow_name = "callback_workflow"

    # Root span
    response1 = litellm.completion(
        api_key=api_key,
        api_base=API_BASE,
        model=MODEL,
        stream=True,
        messages=[{"role": "user", "content": "Say hello in one word."}],
        metadata={
            "keywordsai_params": {
                "trace_id": trace_id,
                "span_id": root_span_id,
                "workflow_name": workflow_name,
                "span_name": "callback_root_generation",
                "customer_identifier": "test_callback_user",
            }
        },
    )
    chunks1 = list(response1)
    assert len(chunks1) > 0
    response1_text = _extract_stream_text(chunks1) or "Hello"

    # Child span
    response2 = litellm.completion(
        api_key=api_key,
        api_base=API_BASE,
        model=MODEL,
        messages=[
            {"role": "user", "content": "Say hello in one word."},
            {"role": "assistant", "content": response1_text},
            {"role": "user", "content": "Now say goodbye in one word."},
        ],
        metadata={
            "keywordsai_params": {
                "trace_id": trace_id,
                "span_id": child_span_id,
                "parent_span_id": root_span_id,
                "workflow_name": workflow_name,
                "span_name": "callback_child_generation",
                "customer_identifier": "test_callback_user",
            }
        },
    )
    assert response2.choices[0].message.content


def test_trace_with_callback_streaming(callback, api_key):
    """Test trace with callback mode: root span -> child span.
    
    Uses KeywordsAI gateway for LLM calls + callback for trace logging.
    Trace structure:
        callback_workflow (trace)
        └── callback_root_generation (root span)
            └── callback_child_generation (child span)
    """
    trace_id = uuid.uuid4().hex
    root_span_id = uuid.uuid4().hex[:16]
    child_span_id = uuid.uuid4().hex[:16]
    workflow_name = "callback_workflow"

    # Root span
    response1 = litellm.completion(
        api_key=api_key,
        api_base=API_BASE,
        model=MODEL,
        stream=True,
        messages=[{"role": "user", "content": "Say hello in one word."}],
        metadata={
            "keywordsai_params": {
                "trace_id": trace_id,
                "span_id": root_span_id,
                "workflow_name": workflow_name,
                "span_name": "callback_root_generation",
                "customer_identifier": "test_callback_user",
            }
        },
    )
    chunks1 = list(response1)
    assert len(chunks1) > 0
    response1_text = _extract_stream_text(chunks1) or "Hello"

    # Child span
    response2 = litellm.completion(
        api_key=api_key,
        api_base=API_BASE,
        model=MODEL,
        stream=True,
        messages=[
            {"role": "user", "content": "Say hello in one word."},
            {"role": "assistant", "content": response1_text},
            {"role": "user", "content": "Now say goodbye in one word."},
        ],
        metadata={
            "keywordsai_params": {
                "trace_id": trace_id,
                "span_id": child_span_id,
                "parent_span_id": root_span_id,
                "workflow_name": workflow_name,
                "span_name": "callback_child_generation",
                "customer_identifier": "test_callback_user",
            }
        },
    )
    chunks2 = list(response2)
    assert len(chunks2) > 0
    assert _extract_stream_text(chunks2)


def test_trace_with_proxy(api_key):
    """Test trace with proxy mode: root span -> child span.
    
    Uses KeywordsAI gateway with extra_body for trace logging (no callback).
    Trace structure:
        proxy_workflow (trace)
        └── proxy_root_generation (root span)
            └── proxy_child_generation (child span)
    """
    trace_id = uuid.uuid4().hex
    root_span_id = uuid.uuid4().hex[:16]
    child_span_id = uuid.uuid4().hex[:16]
    workflow_name = "proxy_workflow"

    # Root span
    response1 = litellm.completion(
        api_key=api_key,
        api_base=API_BASE,
        model=MODEL,
        messages=[{"role": "user", "content": "Say hello in one word."}],
        extra_body={
            "trace_unique_id": trace_id,
            "span_unique_id": root_span_id,
            "span_workflow_name": workflow_name,
            "span_name": "proxy_root_generation",
            "customer_identifier": "test_proxy_user",
        },
    )
    assert response1.choices[0].message.content

    # Child span
    response2 = litellm.completion(
        api_key=api_key,
        api_base=API_BASE,
        model=MODEL,
        messages=[
            {"role": "user", "content": "Say hello in one word."},
            {"role": "assistant", "content": response1.choices[0].message.content},
            {"role": "user", "content": "Now say goodbye in one word."},
        ],
        extra_body={
            "trace_unique_id": trace_id,
            "span_unique_id": child_span_id,
            "span_parent_id": root_span_id,
            "span_workflow_name": workflow_name,
            "span_name": "proxy_child_generation",
            "customer_identifier": "test_proxy_user",
        },
    )
    assert response2.choices[0].message.content

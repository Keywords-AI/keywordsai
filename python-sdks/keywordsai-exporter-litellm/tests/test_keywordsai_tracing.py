"""Test tracing functionality for Keywords AI LiteLLM integration.

Tests cover:
1. KeywordsAILiteLLMCallback - LiteLLM-native callback with trace hierarchy
2. Proxy mode - Direct API routing through Keywords AI
"""

import os
import sys
import time
import uuid
from datetime import datetime, timezone

import litellm
import pytest

from keywordsai_exporter_litellm import KeywordsAILiteLLMCallback

KEYWORDSAI_API_BASE = "https://api.keywordsai.co/api/"
DEFAULT_MODEL = "gpt-4o-mini"


@pytest.fixture
def api_key():
    """Get Keywords AI API key from environment."""
    key = os.getenv("KEYWORDSAI_API_KEY")
    if not key:
        pytest.skip("KEYWORDSAI_API_KEY not set")
    return key


@pytest.fixture
def callback(api_key):
    """Setup LiteLLM with KeywordsAILiteLLMCallback."""
    cb = KeywordsAILiteLLMCallback(api_key=api_key)
    litellm.success_callback = [cb.log_success_event]
    litellm.failure_callback = [cb.log_failure_event]
    yield cb
    litellm.success_callback = []
    litellm.failure_callback = []


class TestCallbackTracing:
    """Test tracing with KeywordsAILiteLLMCallback."""

    def test_nested_spans(self, callback, api_key):
        """Test nested spans with callback. Structure: workflow -> 3 generations."""
        litellm.api_base = KEYWORDSAI_API_BASE
        
        trace_id = uuid.uuid4().hex
        workflow_span_id = uuid.uuid4().hex[:16]
        workflow_start = datetime.now(timezone.utc)
        
        base_params = {
            "trace_id": trace_id,
            "parent_span_id": workflow_span_id,
            "customer_identifier": "test_callback",
            "workflow_name": "multi_step_agent",
        }
        
        # Step 1: Analyze
        r1 = litellm.completion(
            api_key=api_key,
            model=DEFAULT_MODEL,
            messages=[{"role": "user", "content": "What is 3+3? Just the number."}],
            metadata={"keywordsai_params": {**base_params, "span_name": "step1_analyze"}},
        )
        
        # Step 2: Verify
        r2 = litellm.completion(
            api_key=api_key,
            model=DEFAULT_MODEL,
            messages=[{"role": "user", "content": f"Is {r1.choices[0].message.content} correct for 3+3? Yes/no."}],
            metadata={"keywordsai_params": {**base_params, "span_name": "step2_verify"}},
        )
        
        # Step 3: Summarize
        r3 = litellm.completion(
            api_key=api_key,
            model=DEFAULT_MODEL,
            messages=[{"role": "user", "content": "Say 'done' in one word."}],
            metadata={"keywordsai_params": {**base_params, "span_name": "step3_summarize"}},
        )
        
        # Send workflow span
        time.sleep(1.0)
        callback.send_workflow_span(
            trace_id=trace_id,
            span_id=workflow_span_id,
            workflow_name="multi_step_agent",
            start_time=workflow_start,
            end_time=datetime.now(timezone.utc),
            customer_identifier="test_callback",
        )
        
        assert all(r is not None for r in [r1, r2, r3])


class TestProxyTracing:
    """Test tracing with Keywords AI Proxy mode."""

    def test_nested_spans(self, callback, api_key):
        """Test nested spans with proxy. Structure: workflow -> 3 generations."""
        litellm.api_base = KEYWORDSAI_API_BASE
        
        trace_id = uuid.uuid4().hex
        workflow_span_id = uuid.uuid4().hex[:16]
        workflow_start = datetime.now(timezone.utc)
        
        base_params = {
            "trace_id": trace_id,
            "parent_span_id": workflow_span_id,
            "customer_identifier": "test_proxy",
            "workflow_name": "proxy_workflow",
        }
        
        # Step 1
        r1 = litellm.completion(
            api_key=api_key,
            model=DEFAULT_MODEL,
            messages=[{"role": "user", "content": "What is 4+4? Just the number."}],
            metadata={"keywordsai_params": {**base_params, "span_name": "step1"}},
            extra_body={"customer_identifier": "test_proxy"},
        )
        
        # Step 2
        r2 = litellm.completion(
            api_key=api_key,
            model=DEFAULT_MODEL,
            messages=[{"role": "user", "content": f"Is {r1.choices[0].message.content} correct for 4+4? Yes/no."}],
            metadata={"keywordsai_params": {**base_params, "span_name": "step2"}},
            extra_body={"customer_identifier": "test_proxy"},
        )
        
        # Step 3
        r3 = litellm.completion(
            api_key=api_key,
            model=DEFAULT_MODEL,
            messages=[{"role": "user", "content": "Say 'complete' in one word."}],
            metadata={"keywordsai_params": {**base_params, "span_name": "step3"}},
            extra_body={"customer_identifier": "test_proxy"},
        )
        
        # Send workflow span
        time.sleep(1.0)
        callback.send_workflow_span(
            trace_id=trace_id,
            span_id=workflow_span_id,
            workflow_name="proxy_workflow",
            start_time=workflow_start,
            end_time=datetime.now(timezone.utc),
            customer_identifier="test_proxy",
        )
        
        assert all(r is not None for r in [r1, r2, r3])


if __name__ == "__main__":
    key = os.getenv("KEYWORDSAI_API_KEY")
    if not key:
        print("Please set KEYWORDSAI_API_KEY environment variable")
        sys.exit(1)
    
    print("Running manual trace test...")
    
    cb = KeywordsAILiteLLMCallback(api_key=key)
    litellm.success_callback = [cb.log_success_event]
    litellm.failure_callback = [cb.log_failure_event]
    litellm.api_base = KEYWORDSAI_API_BASE
    
    trace_id = uuid.uuid4().hex
    workflow_span_id = uuid.uuid4().hex[:16]
    workflow_start = datetime.now(timezone.utc)
    
    params = {"trace_id": trace_id, "parent_span_id": workflow_span_id, "workflow_name": "manual_test"}
    
    r1 = litellm.completion(
        api_key=key,
        model=DEFAULT_MODEL,
        messages=[{"role": "user", "content": "Say 'step 1 done'"}],
        metadata={"keywordsai_params": {**params, "span_name": "step_1"}},
    )
    print(f"Step 1: {r1.choices[0].message.content}")
    
    r2 = litellm.completion(
        api_key=key,
        model=DEFAULT_MODEL,
        messages=[{"role": "user", "content": "Say 'step 2 done'"}],
        metadata={"keywordsai_params": {**params, "span_name": "step_2"}},
    )
    print(f"Step 2: {r2.choices[0].message.content}")
    
    time.sleep(1.0)
    cb.send_workflow_span(
        trace_id=trace_id,
        span_id=workflow_span_id,
        workflow_name="manual_test",
        start_time=workflow_start,
        end_time=datetime.now(timezone.utc),
    )
    
    print("Test completed!")

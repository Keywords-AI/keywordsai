"""Test tracing functionality for Keywords AI LiteLLM integration.

Tests cover two integration methods:
1. KeywordsAILiteLLMCallback - LiteLLM-native callback
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

# Constants
KEYWORDSAI_API_BASE = "https://api.keywordsai.co/api/"
DEFAULT_MODEL = "gpt-4o-mini"


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def keywordsai_api_key():
    """Get Keywords AI API key from environment."""
    api_key = os.getenv("KEYWORDSAI_API_KEY")
    if not api_key:
        pytest.skip("KEYWORDSAI_API_KEY not set")
    return api_key


@pytest.fixture
def setup_callback(keywordsai_api_key):
    """Setup LiteLLM with KeywordsAILiteLLMCallback."""
    callback = KeywordsAILiteLLMCallback(api_key=keywordsai_api_key)
    litellm.success_callback = [callback.log_success_event]
    litellm.failure_callback = [callback.log_failure_event]
    yield callback
    litellm.success_callback = []
    litellm.failure_callback = []


# =============================================================================
# Test Classes
# =============================================================================

class TestTracingWithCallback:
    """Test tracing with KeywordsAILiteLLMCallback (LiteLLM-native)."""

    def test_nested_spans_callback(self, setup_callback, keywordsai_api_key):
        """Test nested spans with callback method.

        Structure: workflow -> generation1, generation2, generation3
        """
        litellm.api_base = KEYWORDSAI_API_BASE

        # Generate trace identifiers
        trace_id = uuid.uuid4().hex
        workflow_span_id = uuid.uuid4().hex[:16]
        workflow_start = datetime.now(timezone.utc)

        print(f"\nCallback test - trace_id: {trace_id}")

        # Common keywordsai_params
        base_params = {
            "trace_id": trace_id,
            "parent_span_id": workflow_span_id,
            "customer_identifier": "test_callback",
            "workflow_name": "multi_step_agent_callback",
        }

        # Step 1
        response1 = litellm.completion(
            api_key=keywordsai_api_key,
            model=DEFAULT_MODEL,
            messages=[{"role": "user", "content": "What is 3+3? Answer with just the number."}],
            metadata={"keywordsai_params": {**base_params, "span_name": "step1.analyze"}}
        )
        step1_result = response1.choices[0].message.content
        print(f"Step 1: {step1_result}")

        # Step 2
        response2 = litellm.completion(
            api_key=keywordsai_api_key,
            model=DEFAULT_MODEL,
            messages=[{"role": "user", "content": f"Is {step1_result} correct for 3+3? Yes or no."}],
            metadata={"keywordsai_params": {**base_params, "span_name": "step2.verify"}}
        )
        step2_result = response2.choices[0].message.content
        print(f"Step 2: {step2_result}")

        # Step 3
        response3 = litellm.completion(
            api_key=keywordsai_api_key,
            model=DEFAULT_MODEL,
            messages=[{"role": "user", "content": f"Summary: 3+3={step1_result}, verified={step2_result}. One word."}],
            metadata={"keywordsai_params": {**base_params, "span_name": "step3.summarize"}}
        )
        print(f"Step 3: {response3.choices[0].message.content}")

        # Wait for spans to be sent, then send workflow span
        time.sleep(1.0)
        setup_callback.send_workflow_span(
            trace_id=trace_id,
            span_id=workflow_span_id,
            workflow_name="multi_step_agent_callback",
            start_time=workflow_start,
            end_time=datetime.now(timezone.utc),
            customer_identifier="test_callback",
        )

        assert all(r is not None for r in [response1, response2, response3])
        print(f"Callback test completed - trace_id: {trace_id}")


class TestTracingWithProxy:
    """Test tracing with Keywords AI Proxy mode."""

    def test_nested_spans_proxy(self, setup_callback, keywordsai_api_key):
        """Test nested spans with proxy method.

        Structure: workflow -> generation1, generation2, generation3
        """
        litellm.api_base = KEYWORDSAI_API_BASE

        # Generate trace identifiers
        trace_id = uuid.uuid4().hex
        workflow_span_id = uuid.uuid4().hex[:16]
        workflow_start = datetime.now(timezone.utc)

        print(f"\nProxy test - trace_id: {trace_id}")

        # Common params
        base_params = {
            "trace_id": trace_id,
            "parent_span_id": workflow_span_id,
            "customer_identifier": "test_proxy",
            "workflow_name": "multi_step_agent_proxy",
        }

        # Step 1
        response1 = litellm.completion(
            api_key=keywordsai_api_key,
            model=DEFAULT_MODEL,
            messages=[{"role": "user", "content": "What is 4+4? Answer with just the number."}],
            metadata={"keywordsai_params": {**base_params, "span_name": "step1.analyze"}},
            extra_body={"customer_identifier": "test_proxy"}
        )
        step1_result = response1.choices[0].message.content
        print(f"Step 1: {step1_result}")

        # Step 2
        response2 = litellm.completion(
            api_key=keywordsai_api_key,
            model=DEFAULT_MODEL,
            messages=[{"role": "user", "content": f"Is {step1_result} correct for 4+4? Yes or no."}],
            metadata={"keywordsai_params": {**base_params, "span_name": "step2.verify"}},
            extra_body={"customer_identifier": "test_proxy"}
        )
        step2_result = response2.choices[0].message.content
        print(f"Step 2: {step2_result}")

        # Step 3
        response3 = litellm.completion(
            api_key=keywordsai_api_key,
            model=DEFAULT_MODEL,
            messages=[{"role": "user", "content": f"Summary: 4+4={step1_result}, verified={step2_result}. One word."}],
            metadata={"keywordsai_params": {**base_params, "span_name": "step3.summarize"}},
            extra_body={"customer_identifier": "test_proxy"}
        )
        print(f"Step 3: {response3.choices[0].message.content}")

        # Wait for spans to be sent, then send workflow span
        time.sleep(1.0)
        setup_callback.send_workflow_span(
            trace_id=trace_id,
            span_id=workflow_span_id,
            workflow_name="multi_step_agent_proxy",
            start_time=workflow_start,
            end_time=datetime.now(timezone.utc),
            customer_identifier="test_proxy",
        )

        assert all(r is not None for r in [response1, response2, response3])
        print(f"Proxy test completed - trace_id: {trace_id}")


# =============================================================================
# Main (for manual testing)
# =============================================================================

if __name__ == "__main__":
    api_key = os.getenv("KEYWORDSAI_API_KEY")
    if not api_key:
        print("Please set KEYWORDSAI_API_KEY environment variable")
        sys.exit(1)

    print("Running manual trace test with callback...")

    callback = KeywordsAILiteLLMCallback(api_key=api_key)
    litellm.success_callback = [callback.log_success_event]
    litellm.failure_callback = [callback.log_failure_event]
    litellm.api_base = KEYWORDSAI_API_BASE

    # Generate trace identifiers
    trace_id = uuid.uuid4().hex
    workflow_span_id = uuid.uuid4().hex[:16]
    workflow_start = datetime.now(timezone.utc)

    base_params = {
        "trace_id": trace_id,
        "parent_span_id": workflow_span_id,
        "workflow_name": "test_main_workflow",
    }

    r1 = litellm.completion(
        api_key=api_key,
        model=DEFAULT_MODEL,
        messages=[{"role": "user", "content": "Say 'step 1 complete'"}],
        metadata={"keywordsai_params": {**base_params, "span_name": "step_1"}}
    )
    print(f"Step 1: {r1.choices[0].message.content}")

    r2 = litellm.completion(
        api_key=api_key,
        model=DEFAULT_MODEL,
        messages=[{"role": "user", "content": "Say 'step 2 complete'"}],
        metadata={"keywordsai_params": {**base_params, "span_name": "step_2"}}
    )
    print(f"Step 2: {r2.choices[0].message.content}")

    time.sleep(1.0)
    callback.send_workflow_span(
        trace_id=trace_id,
        span_id=workflow_span_id,
        workflow_name="test_main_workflow",
        start_time=workflow_start,
        end_time=datetime.now(timezone.utc),
    )

    print("\nTest completed!")

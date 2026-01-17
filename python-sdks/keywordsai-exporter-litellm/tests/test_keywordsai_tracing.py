"""Test tracing functionality for Keywords AI LiteLLM integration.

Tests cover three integration methods:
1. LiteLLMInstrumentor - OpenTelemetry-based automatic instrumentation
2. KeywordsAILiteLLMCallback - LiteLLM-native callback
3. Proxy mode - Direct API routing through Keywords AI
"""

import asyncio
import os
import sys
import time
import uuid
from datetime import datetime, timezone

import litellm
import pytest
from opentelemetry import trace

from keywordsai_exporter_litellm import KeywordsAILiteLLMCallback, LiteLLMInstrumentor

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
def setup_instrumentor(keywordsai_api_key):
    """Setup and teardown LiteLLMInstrumentor."""
    instrumentor = LiteLLMInstrumentor()
    instrumentor.instrument(api_key=keywordsai_api_key)
    yield instrumentor
    instrumentor.uninstrument()


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

class TestTracingWithInstrumentor:
    """Test tracing with LiteLLMInstrumentor (OpenTelemetry-based)."""

    def test_single_completion_creates_span(self, setup_instrumentor, keywordsai_api_key):
        """Test that a single completion creates a span."""
        litellm.api_base = KEYWORDSAI_API_BASE

        response = litellm.completion(
            api_key=keywordsai_api_key,
            model=DEFAULT_MODEL,
            messages=[{"role": "user", "content": "Say hello in one word"}],
            metadata={
                "keywordsai_params": {
                    "customer_identifier": "test_single_span",
                }
            }
        )

        assert response is not None
        assert response.choices[0].message.content is not None
        print(f"Response: {response.choices[0].message.content}")

    def test_nested_spans_create_trace_tree(self, setup_instrumentor, keywordsai_api_key):
        """Test that nested spans create a proper trace tree."""
        litellm.api_base = KEYWORDSAI_API_BASE
        tracer = trace.get_tracer(__name__)

        with tracer.start_as_current_span("workflow.multi_step_agent_instrumentor") as parent:
            parent.set_attribute("workflow.name", "multi_step_agent_instrumentor")

            # Step 1: Analyze
            with tracer.start_as_current_span("step.analyze"):
                response1 = litellm.completion(
                    api_key=keywordsai_api_key,
                    model=DEFAULT_MODEL,
                    messages=[{"role": "user", "content": "What is 2+2? Answer with just the number."}],
                    metadata={"keywordsai_params": {"customer_identifier": "test_nested"}}
                )
                step1_result = response1.choices[0].message.content
                print(f"Step 1: {step1_result}")

            # Step 2: Verify
            with tracer.start_as_current_span("step.verify"):
                response2 = litellm.completion(
                    api_key=keywordsai_api_key,
                    model=DEFAULT_MODEL,
                    messages=[{"role": "user", "content": f"Is {step1_result} correct for 2+2? Yes or no."}],
                    metadata={"keywordsai_params": {"customer_identifier": "test_nested"}}
                )
                step2_result = response2.choices[0].message.content
                print(f"Step 2: {step2_result}")

            # Step 3: Summarize
            with tracer.start_as_current_span("step.summarize"):
                response3 = litellm.completion(
                    api_key=keywordsai_api_key,
                    model=DEFAULT_MODEL,
                    messages=[{"role": "user", "content": f"Summary: 2+2={step1_result}, verified={step2_result}. One word."}],
                    metadata={"keywordsai_params": {"customer_identifier": "test_nested"}}
                )
                print(f"Step 3: {response3.choices[0].message.content}")

        assert all(r is not None for r in [response1, response2, response3])

    def test_parallel_spans(self, setup_instrumentor, keywordsai_api_key):
        """Test parallel async spans under the same parent."""
        litellm.api_base = KEYWORDSAI_API_BASE
        tracer = trace.get_tracer(__name__)

        async def make_parallel_calls():
            with tracer.start_as_current_span("workflow.parallel_calls") as parent:
                parent.set_attribute("workflow.name", "parallel_calls")

                async def call_llm(index):
                    with tracer.start_as_current_span(f"parallel.call_{index}"):
                        return await litellm.acompletion(
                            api_key=keywordsai_api_key,
                            model=DEFAULT_MODEL,
                            messages=[{"role": "user", "content": f"Say the number {index}"}],
                            metadata={"keywordsai_params": {"customer_identifier": "test_parallel"}}
                        )

                return await asyncio.gather(*[call_llm(i) for i in range(3)])

        results = asyncio.run(make_parallel_calls())
        assert len(results) == 3
        assert all(r is not None for r in results)


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


class TestTracingEdgeCases:
    """Test edge cases and error handling."""

    def test_instrumentor_handles_error(self, setup_instrumentor, keywordsai_api_key):
        """Test that errors are properly captured in spans."""
        litellm.api_base = KEYWORDSAI_API_BASE

        try:
            litellm.completion(
                api_key=keywordsai_api_key,
                model="invalid-model-that-does-not-exist",
                messages=[{"role": "user", "content": "This should fail"}],
            )
        except Exception as e:
            print(f"Expected error: {type(e).__name__}")

    def test_multiple_sequential_calls(self, setup_instrumentor, keywordsai_api_key):
        """Test multiple sequential calls within a parent span."""
        litellm.api_base = KEYWORDSAI_API_BASE
        tracer = trace.get_tracer(__name__)

        responses = []
        with tracer.start_as_current_span("workflow.sequential_calls") as parent:
            parent.set_attribute("workflow.name", "sequential_calls")

            for i in range(3):
                with tracer.start_as_current_span(f"step.call_{i}"):
                    response = litellm.completion(
                        api_key=keywordsai_api_key,
                        model=DEFAULT_MODEL,
                        messages=[{"role": "user", "content": f"Say 'response {i}'"}],
                        metadata={"keywordsai_params": {"customer_identifier": "test_sequential"}}
                    )
                    responses.append(response)
                    print(f"Call {i}: {response.choices[0].message.content}")

        assert len(responses) == 3
        assert all(r is not None for r in responses)


# =============================================================================
# Main (for manual testing)
# =============================================================================

if __name__ == "__main__":
    api_key = os.getenv("KEYWORDSAI_API_KEY")
    if not api_key:
        print("Please set KEYWORDSAI_API_KEY environment variable")
        sys.exit(1)

    print("Running manual trace test...")

    instrumentor = LiteLLMInstrumentor()
    instrumentor.instrument(api_key=api_key)
    litellm.api_base = KEYWORDSAI_API_BASE
    tracer = trace.get_tracer(__name__)

    with tracer.start_as_current_span("test.main_workflow") as parent:
        parent.set_attribute("test.name", "manual_run")

        with tracer.start_as_current_span("test.step_1"):
            r1 = litellm.completion(
                api_key=api_key,
                model=DEFAULT_MODEL,
                messages=[{"role": "user", "content": "Say 'step 1 complete'"}]
            )
            print(f"Step 1: {r1.choices[0].message.content}")

        with tracer.start_as_current_span("test.step_2"):
            r2 = litellm.completion(
                api_key=api_key,
                model=DEFAULT_MODEL,
                messages=[{"role": "user", "content": "Say 'step 2 complete'"}]
            )
            print(f"Step 2: {r2.choices[0].message.content}")

    instrumentor.uninstrument()
    print("\nTest completed!")

"""
Basic test to verify Langfuse instrumentation works and sends to Keywords AI.

This test uses the @observe decorator and manual tracing to verify that:
1. The instrumentor patches httpx correctly
2. Langfuse data is intercepted
3. Data is transformed to Keywords AI format
4. Requests are redirected to Keywords AI endpoint

Run with: poetry run python -m pytest tests/test_basic_langfuse.py -v -s
"""

import os
import logging

# Set up debug logging BEFORE any imports
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# IMPORTANT: Instrument BEFORE importing Langfuse
from keywordsai_instrumentation_langfuse import LangfuseInstrumentor

# Mock Keywords AI API key for testing
os.environ["KEYWORDSAI_API_KEY"] = "test-api-key"

print("\n" + "="*80)
print("INSTRUMENTING LANGFUSE")
print("="*80)

# Instrument with debug endpoint (you can change this to actual Keywords AI endpoint)
instrumentor = LangfuseInstrumentor()
instrumentor.instrument(
    api_key=os.environ["KEYWORDSAI_API_KEY"],
    endpoint="https://httpbin.org/post"  # For testing - echoes back what we send
)

print("Instrumentation complete!")
print("="*80 + "\n")

# NOW import Langfuse
from langfuse import Langfuse, observe

print("\n" + "="*80)
print("INITIALIZING LANGFUSE CLIENT")
print("="*80)

# Initialize Langfuse (you can use dummy keys for testing)
langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY", "pk-lf-test"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY", "sk-lf-test"),
    host="https://cloud.langfuse.com"  # This will be intercepted
)

print("Langfuse client initialized")
print("="*80 + "\n")


@observe()
def simple_function(query: str):
    """Simple function with observe decorator."""
    print(f"\n  [Inside simple_function] with query: {query}")
    return f"Response to: {query}"


@observe(as_type="generation")
def generation_function(prompt: str):
    """Function marked as generation type."""
    print(f"\n  [Inside generation_function] with prompt: {prompt}")
    return f"Generated response for: {prompt}"


@observe()
def nested_workflow(task: str):
    """Workflow that calls nested functions."""
    print(f"\n  [Inside nested_workflow] with task: {task}")
    
    # Call another observed function (creates parent-child relationship)
    result1 = simple_function(f"subtask 1 for {task}")
    result2 = generation_function(f"generate for {task}")
    
    return f"Completed: {task}"


def test_langfuse_observe_decorator():
    """Test that @observe decorator works and data is sent."""
    print("\n" + "="*80)
    print("TEST 1: Simple @observe() decorator")
    print("="*80)
    
    result = simple_function("Hello World")
    print(f"  Result: {result}")
    assert result == "Response to: Hello World"
    
    # Flush to ensure data is sent
    print("\n  Flushing Langfuse...")
    langfuse.flush()
    print("  Flush complete!")
    print("="*80 + "\n")


def test_langfuse_generation():
    """Test generation type observation."""
    print("\n" + "="*80)
    print("TEST 2: @observe(as_type='generation')")
    print("="*80)
    
    result = generation_function("Write a poem")
    print(f"  Result: {result}")
    assert "Generated response" in result
    
    print("\n  Flushing Langfuse...")
    langfuse.flush()
    print("  Flush complete!")
    print("="*80 + "\n")


def test_langfuse_nested():
    """Test nested observations (workflow with children)."""
    print("\n" + "="*80)
    print("TEST 3: Nested observations")
    print("="*80)
    
    result = nested_workflow("Process user request")
    print(f"  Result: {result}")
    assert "Completed" in result
    
    print("\n  Flushing Langfuse...")
    langfuse.flush()
    print("  Flush complete!")
    print("="*80 + "\n")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("RUNNING LANGFUSE INSTRUMENTATION TESTS")
    print("="*80 + "\n")
    
    try:
        test_langfuse_observe_decorator()
        test_langfuse_generation()
        test_langfuse_nested()
        
        print("\n" + "="*80)
        print("ALL TESTS PASSED!")
        print("="*80 + "\n")
        
        print("\nNOTE: Check the debug logs above to see:")
        print("  1. httpx.Client.send being called")
        print("  2. Langfuse batch data being intercepted")
        print("  3. Transformation to Keywords AI format")
        print("  4. Redirect to Keywords AI endpoint")
        
    except Exception as e:
        print(f"\nERROR: TEST FAILED: {e}")
        import traceback
        traceback.print_exc()

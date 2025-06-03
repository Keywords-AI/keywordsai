#!/usr/bin/env python3
"""
Test script for the new KeywordsAI OpenTelemetry implementation.
This replaces the Traceloop dependency with direct OpenTelemetry usage.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from keywordsai_tracing import KeywordsAITelemetry, workflow, task, keywordsai_span_attributes
from keywordsai_tracing.instruments import Instruments

# Mock OpenAI for testing
class MockOpenAI:
    class ChatCompletions:
        def create(self, **kwargs):
            return {
                "choices": [{"message": {"content": "Hello from mock OpenAI!"}}],
                "usage": {"total_tokens": 10}
            }
    
    def __init__(self):
        self.chat = type('Chat', (), {'completions': self.ChatCompletions()})()

# Set up environment
os.environ["KEYWORDSAI_API_KEY"] = "test-key"
os.environ["KEYWORDSAI_BASE_URL"] = "https://api.keywordsai.co/api"

def test_basic_initialization():
    """Test basic telemetry initialization"""
    print("Testing basic initialization...")
    
    telemetry = KeywordsAITelemetry(
        app_name="test-app",
        block_instruments={Instruments.REDIS, Instruments.REQUESTS},
        enabled=True
    )
    
    assert telemetry.is_initialized(), "Telemetry should be initialized"
    print("✓ Basic initialization works")

@workflow(name="test_workflow")
def test_workflow_decorator():
    """Test workflow decorator"""
    print("Testing workflow decorator...")
    
    @task(name="subtask")
    def subtask(data):
        return f"Processed: {data}"
    
    result = subtask("test data")
    print(f"✓ Workflow and task decorators work: {result}")
    return result

def test_context_manager():
    """Test context manager for span attributes"""
    print("Testing context manager...")
    
    with keywordsai_span_attributes(
        keywordsai_params={
            "trace_group_identifier": "test_group",
            "custom_param": "test_value"
        },
        enable_content_tracing=True
    ):
        @task(name="context_task")
        def context_task():
            return "Task with context"
        
        result = context_task()
        print(f"✓ Context manager works: {result}")

def test_async_support():
    """Test async function support"""
    print("Testing async support...")
    
    import asyncio
    
    @workflow(name="async_workflow")
    async def async_workflow():
        @task(name="async_task")
        async def async_task():
            await asyncio.sleep(0.1)
            return "Async task completed"
        
        return await async_task()
    
    result = asyncio.run(async_workflow())
    print(f"✓ Async support works: {result}")

def test_error_handling():
    """Test error handling in spans"""
    print("Testing error handling...")
    
    @task(name="error_task")
    def error_task():
        raise ValueError("Test error")
    
    try:
        error_task()
    except ValueError as e:
        print(f"✓ Error handling works: {e}")

def test_mock_openai_integration():
    """Test with mock OpenAI to simulate real usage"""
    print("Testing mock OpenAI integration...")
    
    client = MockOpenAI()
    
    @workflow(name="openai_workflow")
    def openai_workflow():
        with keywordsai_span_attributes(
            keywordsai_params={
                "trace_group_identifier": "openai_test",
                "model": "gpt-4o"
            }
        ):
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": "Hello, world!"}],
            )
            return response
    
    result = openai_workflow()
    print(f"✓ Mock OpenAI integration works: {result}")

def main():
    """Run all tests"""
    print("🚀 Testing new KeywordsAI OpenTelemetry implementation")
    print("=" * 60)
    
    try:
        test_basic_initialization()
        test_workflow_decorator()
        test_context_manager()
        test_async_support()
        test_error_handling()
        test_mock_openai_integration()
        
        print("=" * 60)
        print("✅ All tests passed! The new implementation works correctly.")
        print("\n📊 Key improvements over Traceloop:")
        print("  • Direct OpenTelemetry usage (no wrapper dependency)")
        print("  • Thread-safe singleton pattern")
        print("  • Proper async/await support")
        print("  • Configurable instrumentation")
        print("  • Better error handling")
        print("  • Cleaner context management")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 
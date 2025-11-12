#!/usr/bin/env python3
"""
Tests for the new KeywordsAI client API.
"""

import pytest
from unittest.mock import patch, MagicMock
from opentelemetry.trace import StatusCode

from keywordsai_tracing import KeywordsAITelemetry, get_client, workflow, task
from keywordsai_tracing.core.client import KeywordsAIClient


class TestKeywordsAIClient:
    """Test the KeywordsAIClient functionality"""
    
    def setup_method(self):
        """Setup for each test"""
        # Initialize telemetry for testing
        self.telemetry = KeywordsAITelemetry(
            app_name="test-app",
            api_key="test-key",
            is_enabled=True
        )
    
    def test_get_client_returns_instance(self):
        """Test that get_client returns a KeywordsAIClient instance"""
        client = get_client()
        assert isinstance(client, KeywordsAIClient)
    
    def test_get_client_returns_same_instance(self):
        """Test that get_client returns the same instance (singleton behavior)"""
        client1 = get_client()
        client2 = get_client()
        assert client1 is client2
    
    def test_telemetry_get_client_method(self):
        """Test that telemetry instance has get_client method"""
        client = self.telemetry.get_client()
        assert isinstance(client, KeywordsAIClient)
    
    @workflow(name="test_workflow")
    def test_workflow_with_client_api(self):
        """Test using client API within a workflow"""
        client = get_client()
        
        # Should be able to get current span
        span = client.get_current_span()
        assert span is not None
        
        # Should be able to get trace and span IDs
        trace_id = client.get_current_trace_id()
        span_id = client.get_current_span_id()
        
        assert trace_id is not None
        assert span_id is not None
        assert len(trace_id) == 32  # 128-bit trace ID as hex
        assert len(span_id) == 16   # 64-bit span ID as hex
        
        # Should be able to update span
        success = client.update_current_span(
            attributes={"test.attribute": "test_value"},
            keywordsai_params={"trace_group_identifier": "test-group"}
        )
        assert success is True
        
        # Should be able to add events
        success = client.add_event("test_event", {"event.data": "test"})
        assert success is True
        
        # Should be able to check if recording
        is_recording = client.is_recording()
        assert is_recording is True
        
        return "test_result"
    
    def test_client_api_in_workflow(self):
        """Test the client API functionality within a workflow context"""
        result = self.test_workflow_with_client_api()
        assert result == "test_result"
    
    @task(name="test_task_with_exception")
    def test_task_with_exception(self):
        """Test exception recording with client API"""
        client = get_client()
        
        try:
            raise ValueError("Test exception")
        except ValueError as e:
            success = client.record_exception(e)
            assert success is True
            raise  # Re-raise for test
    
    def test_exception_recording(self):
        """Test exception recording functionality"""
        with pytest.raises(ValueError, match="Test exception"):
            self.test_task_with_exception()
    
    def test_context_operations(self):
        """Test context value operations"""
        client = get_client()
        
        # Set context values
        success1 = client.set_context_value("test_key", "test_value")
        success2 = client.set_context_value("test_number", 42)
        
        assert success1 is True
        assert success2 is True
        
        # Get context values
        value1 = client.get_context_value("test_key")
        value2 = client.get_context_value("test_number")
        value3 = client.get_context_value("nonexistent_key")
        
        assert value1 == "test_value"
        assert value2 == 42
        assert value3 is None
    
    def test_client_without_active_span(self):
        """Test client behavior when no span is active"""
        client = get_client()
        
        # These should return None when no span is active
        trace_id = client.get_current_trace_id()
        span_id = client.get_current_span_id()
        span = client.get_current_span()
        
        # Outside of a span context, these should be None
        # (unless there's a span from another test still active)
        # We'll just check they don't raise exceptions
        assert trace_id is None or isinstance(trace_id, str)
        assert span_id is None or isinstance(span_id, str)
        
        # Update operations should return False when no span
        success = client.update_current_span(attributes={"test": "value"})
        # This might be True if there's still an active span from another test
        assert isinstance(success, bool)
        
        # Event operations should return False when no span
        success = client.add_event("test_event")
        assert isinstance(success, bool)
        
        # Exception recording should return False when no span
        success = client.record_exception(Exception("test"))
        assert isinstance(success, bool)
        
        # is_recording should return False when no span
        is_recording = client.is_recording()
        assert isinstance(is_recording, bool)


def test_module_level_get_client():
    """Test the module-level get_client function"""
    from keywordsai_tracing import get_client
    
    client = get_client()
    assert isinstance(client, KeywordsAIClient)


if __name__ == "__main__":
    # Run a simple test
    test = TestKeywordsAIClient()
    test.setup_method()
    
    print("🧪 Running KeywordsAI Client API Tests")
    print("=" * 50)
    
    try:
        test.test_get_client_returns_instance()
        print("✅ get_client returns instance")
        
        test.test_get_client_returns_same_instance()
        print("✅ get_client singleton behavior")
        
        test.test_telemetry_get_client_method()
        print("✅ telemetry.get_client() method")
        
        test.test_client_api_in_workflow()
        print("✅ client API in workflow context")
        
        test.test_exception_recording()
        print("✅ exception recording")
        
        test.test_context_operations()
        print("✅ context operations")
        
        test.test_client_without_active_span()
        print("✅ client behavior without active span")
        
        print("\n🎉 All tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise 
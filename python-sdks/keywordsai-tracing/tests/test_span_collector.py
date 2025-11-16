"""
Unit tests for SpanCollector functionality.
"""

import pytest
from unittest.mock import Mock, MagicMock
from opentelemetry.sdk.trace.export import SpanExportResult

from keywordsai_tracing.core.span_collector import SpanCollector, LocalQueueSpanProcessor, _active_span_collector
from keywordsai_tracing import KeywordsAITelemetry, get_client


class TestLocalQueueSpanProcessor:
    """Tests for LocalQueueSpanProcessor"""
    
    def test_routes_to_collector_when_active(self):
        """Test that spans are routed to active collector"""
        # Setup
        original_processor = Mock()
        processor = LocalQueueSpanProcessor(original_processor)
        
        # Create a mock span
        mock_span = Mock()
        mock_span.name = "test_span"
        
        # Create a collector and set it as active
        exporter = Mock()
        collector = SpanCollector("test-trace", exporter)
        collector._is_collecting = True
        
        # Set collector as active
        token = _active_span_collector.set(collector)
        
        try:
            # Process the span
            processor.on_end(mock_span)
            
            # Verify span went to collector, not original processor
            assert len(collector._local_queue) == 1
            assert collector._local_queue[0] == mock_span
            original_processor.on_end.assert_not_called()
        finally:
            # Cleanup
            _active_span_collector.reset(token)
    
    def test_routes_to_original_when_no_collector(self):
        """Test that spans go to original processor when no active collector"""
        # Setup
        original_processor = Mock()
        processor = LocalQueueSpanProcessor(original_processor)
        
        # Create a mock span
        mock_span = Mock()
        mock_span.name = "test_span"
        
        # Process the span (no active collector)
        processor.on_end(mock_span)
        
        # Verify span went to original processor
        original_processor.on_end.assert_called_once_with(mock_span)
    
    def test_forwards_on_start(self):
        """Test that on_start is forwarded to original processor"""
        original_processor = Mock()
        processor = LocalQueueSpanProcessor(original_processor)
        
        mock_span = Mock()
        mock_context = Mock()
        
        processor.on_start(mock_span, mock_context)
        
        original_processor.on_start.assert_called_once_with(mock_span, mock_context)


class TestSpanCollector:
    """Tests for SpanCollector"""
    
    def test_context_manager_sets_active_collector(self):
        """Test that entering context sets active collector"""
        exporter = Mock()
        collector = SpanCollector("test-trace", exporter)
        
        # Before entering context
        assert _active_span_collector.get() is None
        
        # Enter context
        with collector:
            # Inside context, collector should be active
            assert _active_span_collector.get() == collector
            assert collector._is_collecting is True
        
        # After exiting context
        assert _active_span_collector.get() is None
        assert collector._is_collecting is False
    
    def test_create_span_adds_to_queue(self):
        """Test that create_span adds spans to local queue"""
        # Initialize telemetry first
        telemetry = KeywordsAITelemetry(
            app_name="test-app",
            api_key="test-key",
            is_enabled=True,
        )
        
        exporter = Mock()
        collector = SpanCollector("test-trace", exporter)
        
        with collector:
            # Create spans
            collector.create_span("span1", {"attr1": "value1"})
            collector.create_span("span2", {"attr2": "value2"})
            
            # Verify spans were added to queue
            assert collector.get_span_count() == 2
            
            spans = collector.get_all_spans()
            assert len(spans) == 2
            assert spans[0].name == "span1"
            assert spans[1].name == "span2"
    
    def test_export_spans_calls_exporter(self):
        """Test that export_spans calls the exporter"""
        exporter = Mock()
        exporter.export = Mock(return_value=SpanExportResult.SUCCESS)
        
        collector = SpanCollector("test-trace", exporter)
        
        # Add mock spans
        mock_span1 = Mock()
        mock_span2 = Mock()
        collector._local_queue = [mock_span1, mock_span2]
        
        # Export
        result = collector.export_spans()
        
        # Verify
        assert result is True
        exporter.export.assert_called_once()
        call_args = exporter.export.call_args[0][0]
        assert len(call_args) == 2
    
    def test_export_empty_queue(self):
        """Test exporting with empty queue"""
        exporter = Mock()
        collector = SpanCollector("test-trace", exporter)
        
        # Export empty queue
        result = collector.export_spans()
        
        # Should return True without calling exporter
        assert result is True
        exporter.export.assert_not_called()
    
    def test_clear_spans(self):
        """Test clearing spans from queue"""
        exporter = Mock()
        collector = SpanCollector("test-trace", exporter)
        
        # Add mock spans
        collector._local_queue = [Mock(), Mock(), Mock()]
        assert collector.get_span_count() == 3
        
        # Clear
        collector.clear_spans()
        
        # Verify
        assert collector.get_span_count() == 0
    
    def test_get_span_count(self):
        """Test getting span count"""
        exporter = Mock()
        collector = SpanCollector("test-trace", exporter)
        
        assert collector.get_span_count() == 0
        
        collector._local_queue = [Mock(), Mock()]
        assert collector.get_span_count() == 2


class TestIntegration:
    """Integration tests with KeywordsAIClient"""
    
    def test_client_get_span_collector(self):
        """Test getting span collector from client"""
        # Initialize telemetry
        telemetry = KeywordsAITelemetry(
            app_name="test-app",
            api_key="test-key",
            is_enabled=True,
        )
        
        client = get_client()
        
        # Get span collector
        collector = client.get_span_collector("test-trace")
        
        # Verify
        assert isinstance(collector, SpanCollector)
        assert collector.trace_id == "test-trace"
    
    def test_span_collector_isolation(self):
        """Test that span collector collects ALL spans within its context"""
        # Initialize telemetry
        telemetry = KeywordsAITelemetry(
            app_name="test-app",
            api_key="test-key",
            is_enabled=True,
        )
        
        client = get_client()
        tracer = client.get_tracer()
        
        # Create normal span BEFORE collector (should NOT be collected)
        with tracer.start_as_current_span("span_before_collector") as span:
            span.set_attribute("type", "before")
        
        # Create span collector
        with client.get_span_collector("test-trace") as collector:
            # Create spans in collector
            collector.create_span("collected_span", {"type": "collected"})
            
            # Create normal span WITHIN collector context (WILL be collected)
            with tracer.start_as_current_span("span_within_collector") as span:
                span.set_attribute("type", "within")
            
            # Both spans should be in queue (all spans within context are collected)
            assert collector.get_span_count() == 2
            span_names = [s.name for s in collector.get_all_spans()]
            assert "collected_span" in span_names
            assert "span_within_collector" in span_names
        
        # Create normal span AFTER collector (should NOT be collected)
        with tracer.start_as_current_span("span_after_collector") as span:
            span.set_attribute("type", "after")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


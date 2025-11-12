import pytest
from unittest.mock import Mock, patch
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult
from keywordsai_tracing import KeywordsAITelemetry


class MockExporter(SpanExporter):
    """Mock exporter for testing"""
    
    def __init__(self):
        self.exported_spans = []
    
    def export(self, spans):
        self.exported_spans.extend(spans)
        return SpanExportResult.SUCCESS
    
    def shutdown(self):
        pass
    
    def force_flush(self, timeout_millis=30000):
        return True


def test_custom_exporter_used():
    """Test that custom exporter is used when provided"""
    mock_exporter = MockExporter()
    
    telemetry = KeywordsAITelemetry(
        app_name="test-app",
        custom_exporter=mock_exporter,
        is_enabled=True,
    )
    
    # Create a span
    tracer = telemetry.tracer.get_tracer()
    with tracer.start_as_current_span("test_span") as span:
        span.set_attribute("test", "value")
    
    # Flush to ensure export
    telemetry.flush()
    
    # Verify custom exporter was called
    assert len(mock_exporter.exported_spans) > 0
    assert any(s.name == "test_span" for s in mock_exporter.exported_spans)


def test_default_exporter_when_no_custom():
    """Test that default HTTP exporter is used when no custom exporter provided"""
    with patch('keywordsai_tracing.core.tracer.KeywordsAISpanExporter') as mock_exporter_class:
        telemetry = KeywordsAITelemetry(
            app_name="test-app",
            api_key="test-key",
            base_url="https://test.api",
            is_enabled=True,
        )
        
        # Verify default exporter was created
        mock_exporter_class.assert_called_once()


def test_custom_exporter_ignores_api_settings():
    """Test that api_key and base_url are not used when custom exporter is provided"""
    mock_exporter = MockExporter()
    
    # These should be ignored
    telemetry = KeywordsAITelemetry(
        app_name="test-app",
        api_key="should-be-ignored",
        base_url="https://should-be-ignored",
        custom_exporter=mock_exporter,
        is_enabled=True,
    )
    
    # Should still work with custom exporter
    tracer = telemetry.tracer.get_tracer()
    with tracer.start_as_current_span("test_span"):
        pass
    
    telemetry.flush()
    assert len(mock_exporter.exported_spans) > 0


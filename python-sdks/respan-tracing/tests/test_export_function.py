"""
Simple test to understand and validate the KeywordsAI SDK export function.
This helps understand exactly what data gets exported and in what format.
"""

import json
import os
from unittest.mock import Mock, patch
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import SpanExportResult

# Set up environment for testing
os.environ["KEYWORDSAI_API_KEY"] = "test_key"
os.environ["KEYWORDSAI_BASE_URL"] = "https://test.keywordsai.co/api"

from keywordsai_tracing.main import KeywordsAITelemetry
from keywordsai_tracing.decorators import task, workflow
from keywordsai_tracing.core.exporter import KeywordsAISpanExporter


def test_export_function_basic():
    """
    Test the basic export function to understand what gets exported.
    This is the core export functionality that sends data to KeywordsAI.
    """
    print("\n=== Testing Export Function ===")
    
    # Create a list to capture what gets exported
    exported_data = []
    
    def mock_export(spans):
        """Mock export function that captures the spans being exported"""
        print(f"📤 Export called with {len(spans)} spans")
        
        for i, span in enumerate(spans):
            span_data = {
                "span_name": span.name,
                "trace_id": format(span.context.trace_id, '032x'),
                "span_id": format(span.context.span_id, '016x'),
                "parent_id": format(span.parent.span_id, '016x') if span.parent else None,
                "start_time": span.start_time,
                "end_time": span.end_time,
                "duration_ms": (span.end_time - span.start_time) / 1_000_000,
                "status": {
                    "code": span.status.status_code.name,
                    "description": span.status.description
                },
                "attributes": dict(span.attributes) if span.attributes else {},
                "events": [
                    {
                        "name": event.name,
                        "timestamp": event.timestamp,
                        "attributes": dict(event.attributes) if event.attributes else {}
                    }
                    for event in span.events
                ],
                "resource": dict(span.resource.attributes) if span.resource and span.resource.attributes else {}
            }
            
            exported_data.append(span_data)
            print(f"  Span {i+1}: {span.name}")
            print(f"    Trace ID: {span_data['trace_id']}")
            print(f"    Span ID: {span_data['span_id']}")
            print(f"    Duration: {span_data['duration_ms']:.2f}ms")
            print(f"    Attributes: {len(span_data['attributes'])} items")
            print(f"    Events: {len(span_data['events'])} items")
        
        return SpanExportResult.SUCCESS
    
    # Patch the underlying OTLP exporter to capture exports
    with patch('keywordsai_tracing.core.exporter.OTLPSpanExporter') as mock_otlp:
        mock_exporter = Mock()
        mock_exporter.export = mock_export
        mock_otlp.return_value = mock_exporter
        
        # Initialize telemetry
        telemetry = KeywordsAITelemetry(
            app_name="export_test",
            is_batching_enabled=False  # Use immediate export for testing
        )
        
        # Define test functions
        @task(name="data_processing")
        def process_data(input_text: str) -> dict:
            """Process some data and return structured output"""
            return {
                "processed": input_text.upper(),
                "length": len(input_text),
                "metadata": {"processed_at": "2024-01-01"}
            }
        
        @workflow(name="main_workflow")
        def main_workflow():
            """Main workflow that calls the data processing task"""
            result1 = process_data("hello world")
            result2 = process_data("testing export")
            return {"results": [result1, result2]}
        
        # Execute the workflow
        print("\n🚀 Executing workflow...")
        workflow_result = main_workflow()
        
        # Force flush to ensure all spans are exported
        telemetry.flush()
        
        print(f"\n✅ Workflow completed with result: {workflow_result}")
        print(f"📊 Total spans exported: {len(exported_data)}")
        
        # Analyze what was exported
        print("\n=== EXPORT ANALYSIS ===")
        
        for i, span_data in enumerate(exported_data):
            print(f"\n📋 Span {i+1}: {span_data['span_name']}")
            print(f"   Type: {'Workflow' if 'workflow' in span_data['span_name'] else 'Task'}")
            print(f"   Duration: {span_data['duration_ms']:.2f}ms")
            print(f"   Status: {span_data['status']['code']}")
            
            # Show key attributes
            attrs = span_data['attributes']
            key_attrs = [
                'traceloop.workflow.name',
                'traceloop.entity.path', 
                'traceloop.entity.input',
                'traceloop.entity.output',
                'keywordsai.trace_group_identifier'
            ]
            
            print("   Key Attributes:")
            for attr in key_attrs:
                if attr in attrs:
                    value = attrs[attr]
                    if isinstance(value, str) and len(value) > 100:
                        value = value[:100] + "..."
                    print(f"     {attr}: {value}")
            
            # Show resource info
            if span_data['resource']:
                print("   Resource:")
                for key, value in span_data['resource'].items():
                    print(f"     {key}: {value}")
        
        return exported_data


def test_export_endpoint_configuration():
    """Test how the exporter configures endpoints"""
    print("\n=== Testing Export Endpoint Configuration ===")
    
    test_cases = [
        {
            "input": "https://api.keywordsai.co/api",
            "expected": "https://api.keywordsai.co/api/v1/traces",
            "description": "Standard KeywordsAI API endpoint"
        },
        {
            "input": "https://custom.domain.com",
            "expected": "https://custom.domain.com/v1/traces", 
            "description": "Custom domain"
        },
        {
            "input": "https://api.keywordsai.co/api/v1/traces",
            "expected": "https://api.keywordsai.co/api/v1/traces",
            "description": "Already complete traces endpoint"
        }
    ]
    
    for case in test_cases:
        with patch('keywordsai_tracing.core.exporter.OTLPSpanExporter') as mock_otlp:
            print(f"\n🔗 Testing: {case['description']}")
            print(f"   Input: {case['input']}")
            
            exporter = KeywordsAISpanExporter(
                endpoint=case['input'],
                api_key="test_key"
            )
            
            # Check what endpoint was used
            mock_otlp.assert_called_once()
            call_kwargs = mock_otlp.call_args[1]
            actual_endpoint = call_kwargs['endpoint']
            
            print(f"   Output: {actual_endpoint}")
            print(f"   Expected: {case['expected']}")
            print(f"   ✅ Match: {actual_endpoint == case['expected']}")
            
            # Check headers
            headers = call_kwargs['headers']
            print(f"   Headers: {list(headers.keys())}")
            assert 'Authorization' in headers
            assert headers['Authorization'] == 'Bearer test_key'


def inspect_span_structure():
    """Inspect the structure of ReadableSpan objects to understand what's available for export"""
    print("\n=== Inspecting Span Structure ===")
    
    captured_spans = []
    
    def capture_span(spans):
        captured_spans.extend(spans)
        return SpanExportResult.SUCCESS
    
    with patch('keywordsai_tracing.core.exporter.OTLPSpanExporter') as mock_otlp:
        mock_exporter = Mock()
        mock_exporter.export = capture_span
        mock_otlp.return_value = mock_exporter
        
        telemetry = KeywordsAITelemetry(is_batching_enabled=False)
        
        @task(name="inspection_task")
        def inspection_task():
            return "test_output"
        
        inspection_task()
        telemetry.flush()
        
        if captured_spans:
            span = captured_spans[0]
            print(f"📋 Span object type: {type(span)}")
            print(f"📋 Available attributes on ReadableSpan:")
            
            # List all available attributes and methods
            attributes = [attr for attr in dir(span) if not attr.startswith('_')]
            for attr in sorted(attributes):
                try:
                    value = getattr(span, attr)
                    if callable(value):
                        print(f"   {attr}() - method")
                    else:
                        print(f"   {attr} - {type(value).__name__}")
                except:
                    print(f"   {attr} - (error accessing)")


if __name__ == "__main__":
    # Run the tests
    exported_data = test_export_function_basic()
    test_export_endpoint_configuration()
    inspect_span_structure()
    
    print(f"\n🎯 SUMMARY:")
    print(f"   • The export() function receives ReadableSpan objects")
    print(f"   • Each span contains: name, IDs, timing, status, attributes, events, resource")
    print(f"   • Spans are sent to KeywordsAI's /v1/traces endpoint in OTLP format")
    print(f"   • The exporter handles endpoint building and authentication")
    print(f"   • Total spans captured in test: {len(exported_data)}")
    
    # Save detailed export data for inspection
    with open("export_data_sample.json", "w") as f:
        json.dump(exported_data, f, indent=2, default=str)
    print(f"   • Detailed export data saved to: export_data_sample.json") 
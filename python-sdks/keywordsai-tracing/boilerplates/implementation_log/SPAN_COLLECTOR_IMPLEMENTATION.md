# SpanCollector Implementation Summary

## ✅ Implementation Complete

The `SpanCollector` feature has been successfully implemented to enable batch span collection and manual export control.

### 🎯 What Was Implemented

#### 1. **LocalQueueSpanProcessor** (`src/keywordsai_tracing/core/span_collector.py`)
- Context-aware span processor that routes spans based on active SpanCollector
- Uses Python's `contextvars` for thread-safe context management
- Falls back to original processor when no collector is active
- **Key Insight**: Uses a context variable to track the active collector, allowing selective routing without affecting other spans

#### 2. **SpanCollector Context Manager** (`src/keywordsai_tracing/core/span_collector.py`)
- Collects spans in a local queue instead of auto-exporting
- Provides manual export control via `export_spans()` method
- Automatic cleanup when context exits
- Methods:
  - `create_span(name, attributes)` - Create spans in the local queue
  - `export_spans()` - Batch export all collected spans
  - `get_all_spans()` - Inspect spans before export
  - `get_span_count()` - Get number of collected spans
  - `clear_spans()` - Discard collected spans without exporting

#### 3. **Client Integration** (`src/keywordsai_tracing/core/client.py`)
- Added `get_span_collector(trace_id)` method to `KeywordsAIClient`
- Returns a `SpanCollector` context manager for the specified trace
- Full documentation and examples in docstrings

#### 4. **Tracer Integration** (`src/keywordsai_tracing/core/tracer.py`)
- `LocalQueueSpanProcessor` wraps the existing processor chain
- Exporter reference stored for SpanCollector access
- No breaking changes to existing functionality

#### 5. **Public API** (`src/keywordsai_tracing/__init__.py`)
- Exported `SpanCollector` class for direct import
- Maintains backward compatibility with existing code

### 🔑 Key Design Decision: Context-Based Routing

**Problem**: How to collect only specific spans without affecting all spans globally?

**Solution**: Use Python's `contextvars` module
- The `LocalQueueSpanProcessor` checks for an active `SpanCollector` in the current context
- If found, spans go to that collector's local queue
- If not found, spans go through normal processing (original processor)
- This allows multiple collectors to coexist and only affects spans within their context

**Benefits**:
✅ Thread-safe isolation  
✅ No global state pollution  
✅ Multiple collectors can coexist  
✅ Normal spans unaffected when collector is not active  
✅ Automatic cleanup when context exits

### 📝 Usage Examples

#### Basic Batch Collection

```python
from keywordsai_tracing import get_client

client = get_client()

with client.get_span_collector("trace-123") as collector:
    # Create multiple spans - they go to local queue
    collector.create_span("step1", {"status": "completed", "latency": 100})
    collector.create_span("step2", {"status": "completed", "latency": 200})
    collector.create_span("step3", {"status": "completed", "latency": 150})
    
    # Export all spans as a single batch
    collector.export_spans()
```

#### Async Span Creation (Create Spans After Execution)

```python
# Phase 1: Execute workflows (no tracing context)
results = []
for workflow in workflows:
    result = execute_workflow(workflow)
    results.append(result)

# Phase 2: Create spans from results and export as batch
with client.get_span_collector("exp-123") as collector:
    for i, result in enumerate(results):
        collector.create_span(
            f"workflow_{i}",
            attributes={
                "input": result["input"],
                "output": result["output"],
                "latency": result["latency"],
            }
        )
    
    # Single batch export
    collector.export_spans()
```

#### Span Inspection Before Export

```python
with client.get_span_collector("trace-123") as collector:
    collector.create_span("task1", {"status": "completed"})
    collector.create_span("task2", {"status": "failed"})
    
    # Inspect before export
    print(f"Collected {collector.get_span_count()} spans")
    
    for span in collector.get_all_spans():
        print(f"  - {span.name}: {span.attributes}")
    
    # Decide whether to export
    if collector.get_span_count() > 0:
        collector.export_spans()
```

### 🧪 Testing

**All 11 tests passing** ✅

Test coverage includes:
- LocalQueueSpanProcessor routing logic
- Context variable management
- SpanCollector context manager behavior
- Batch export functionality
- Integration with KeywordsAIClient
- Isolation and thread-safety

Run tests:
```bash
.venv/bin/python -m pytest tests/test_span_collector.py -v
```

### 📁 Files Modified/Created

**New Files**:
- `src/keywordsai_tracing/core/span_collector.py` - Core implementation
- `tests/test_span_collector.py` - Unit and integration tests
- `examples/span_collector_example.py` - Usage examples

**Modified Files**:
- `src/keywordsai_tracing/core/client.py` - Added `get_span_collector()` method
- `src/keywordsai_tracing/core/tracer.py` - Integrated LocalQueueSpanProcessor
- `src/keywordsai_tracing/__init__.py` - Exported SpanCollector
- `src/keywordsai_tracing/core/__init__.py` - Exported SpanCollector and LocalQueueSpanProcessor

### 🎁 Benefits for Backend Workflow System

This implementation directly addresses the requirements in the backend dogfooding proposal:

✅ **Batch Collection → Single Ingestion**: Collect multiple spans and export once  
✅ **Manual Export Control**: No automatic export on span context exit  
✅ **Async Span Creation**: Create spans after execution completes  
✅ **Context Isolation**: Only affects spans within SpanCollector context  
✅ **Thread-Safe**: Uses contextvars for proper isolation  
✅ **Memory Safe**: Automatic cleanup when context exits  
✅ **No Breaking Changes**: Existing code continues to work

### 🔄 Backend Integration Pattern

```python
# In WorkflowExecutionTask
from keywordsai_tracing import get_client

def ingest_workflow_output(workflow_result, trace_id, org, exp_id):
    client = get_client()
    
    # Use SpanCollector for batch collection
    with client.get_span_collector(trace_id) as collector:
        # Create spans from completed workflow results
        collector.create_span(
            "workflow_execution",
            attributes={
                "input": workflow_result["input"],
                "output": workflow_result["output"],
                "experiment_id": exp_id,
                "organization": org,
                "status": "completed"
            }
        )
        
        # Create child spans for workflow steps
        for step in workflow_result["steps"]:
            collector.create_span(
                f"step_{step['name']}",
                attributes={
                    "input": step["input"],
                    "output": step["output"],
                    "latency": step["latency"],
                    "cost": step["cost"],
                }
            )
        
        # Single batch export for entire trace
        collector.export_spans()
```

### 🚀 Next Steps

1. **Backend Integration**: Use SpanCollector in the workflow execution system
2. **Documentation**: Add to SDK documentation and examples
3. **Performance Testing**: Validate batch export performance at scale
4. **Custom Exporters**: Ensure compatibility with backend's custom exporter

### 📚 Additional Resources

- Implementation proposal: `boilerplates/implementation_log/backend_dogfooding_pr_proposal.md`
- Example usage: `examples/span_collector_example.py`
- Tests: `tests/test_span_collector.py`

---

**Status**: ✅ **Ready for Production Use**  
**Tests**: ✅ **All Passing (11/11)**  
**API**: ✅ **Public and Documented**  
**Backward Compatibility**: ✅ **Maintained**


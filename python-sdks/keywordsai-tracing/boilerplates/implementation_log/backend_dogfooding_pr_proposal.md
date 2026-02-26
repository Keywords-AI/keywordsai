# SDK PR Proposal: Manual Span Collection & Batch Export

**Repository:** `https://github.com/Repsan/respan`  
**Path:** `python-sdks/respan-tracing/`  
**Status:** 🚨 **CRITICAL - SDK Enhancement Required for Asynchronous Context Management**

---

## 🚨 Critical Issue: Need Manual Span Collection & Export Control

### **Current Problem: Per-Span Immediate Ingestion**

The current SDK automatically exports each span individually when the `with` context exits:

```python
with tracer.start_as_current_span("step1") as span:
    # Work happens here
    span.set_attributes(...)
# ← Span exported → log_dataset_request call #1

with tracer.start_as_current_span("step2") as span:
    # Work happens here  
    span.set_attributes(...)
# ← Span exported → log_dataset_request call #2

with tracer.start_as_current_span("step3") as span:
    # Work happens here
    span.set_attributes(...)  
# ← Span exported → log_dataset_request call #3

# Result: 3 separate ingestion calls (inefficient)
```

**This creates per-span immediate ingestion** and doesn't support:
1. **Trace-level batching** (collect all spans in a trace, then ingest together)
2. **Manual export control** (ingest only when explicitly requested)
3. **Batch ingestion efficiency** (single ingestion call per trace instead of per-span)

### **Required for Backend Workflow System:**

**Required: Batch Collection → Single Ingestion Pattern:**
```python
# Phase 1: Execute workflows (no spans created yet)
results = []
for workflow in workflows:
    result = execute_workflow(workflow)  # No tracing context
    results.append(result)

# Phase 2: Collect spans in context variable (no ingestion yet)
span_collector = TraceCollector(trace_id="exp-123")
for i, result in enumerate(results):
    span_collector.create_span(f"workflow_{i}", attributes=result)  # Collected only

# Phase 3: Single batch ingestion for entire trace  
span_collector.export_trace()  # One log_dataset_request call for all spans
# Result: 1 ingestion call instead of N separate calls
```

**Key Requirements:**
1. **No automatic ingestion** on span context exit  
2. **Context variable collection** of spans within a trace
3. **Single batch ingestion** of entire trace at once
4. **Trace-level batching** for ingestion efficiency

---

## Current Backend Implementation (Workaround)

We implemented using **context variables** to work around this:

```python
# At app startup (settings.py)
from respan_tracing import RespanTelemetry
from utils.telemetry.backend_exporter import BackendSpanExporter

exporter = BackendSpanExporter()  # Uses context variables internally

RespanTelemetry(
    app_name="respan-backend",
    custom_exporter=exporter,  # ✅ Works
    enabled=True,
)

# Per-request (WorkflowExecutor)
from respan_tracing import get_client
from utils.telemetry import set_telemetry_context

set_telemetry_context(org=org, auth=auth, exp_id=exp_id)  # Set context in ContextVar

client = get_client()  # Get global client
tracer = client.get_tracer()  # ✅ Public API (no longer _tracer private access)

with tracer.start_as_current_span("my_operation"):
    # Exporter reads context from ContextVar when exporting
    pass
```

**This works**, but has limitations:
- ✅ **Solved:** ~~Accessing private `client._tracer` attribute~~ - Now use `client.get_tracer()`
- ❌ **Still an issue:** Still exports each span immediately on context exit
- ❌ **Still an issue:** Cannot batch multiple spans for single ingestion call
- ❌ **Still an issue:** Requires custom `ContextVar` management in `BackendSpanExporter`
- ❌ **Still an issue:** Cannot create spans asynchronously after execution completes

### Why Context Variables Alone Aren't Enough

The current workaround solves **per-request context** (which org/experiment a span belongs to), but doesn't solve **batch collection**:

| Aspect | Context Variables (Current) | SpanCollector (Needed) |
|--------|----------------------------|------------------------|
| **Per-request context** | ✅ Solved via ContextVar | ✅ Maintained |
| **Batch ingestion** | ❌ Each span exported separately | ✅ All spans in one batch |
| **Manual export timing** | ❌ Auto-exports on context exit | ✅ Export when you want |
| **Async span creation** | ❌ Must be in execution context | ✅ Create spans after execution |
| **Memory safety** | ⚠️ Global state requires cleanup | ✅ Local queue dies with context |

---

## 🛠️ Required SDK Enhancements

### 1. **Context Manager + Local Queue - Memory Safe**

**New Context Manager Required:**

```python
# In respan_tracing/core/span_collector.py

from typing import Dict, Any, List, Optional
from contextlib import contextmanager
from opentelemetry.sdk.trace import ReadableSpan

class SpanCollector:
    """
    Context manager for collecting spans in local queue instead of global consumer queue.
    
    Bypasses SDK's auto-consumer by routing spans to local storage,
    enabling manual batch export control.
    """
    
    def __init__(self, trace_id: str, exporter: SpanExporter):
        self.trace_id = trace_id
        self.exporter = exporter
        self._local_queue: List[ReadableSpan] = []
        self._original_processor = None
    
    def __enter__(self):
        """
        Enter context: Replace global processor with local queue processor.
        
        This prevents spans from going to the global consumer queue.
        """
        # Store original processor
        tracer_provider = trace.get_tracer_provider()
        self._original_processor = tracer_provider._active_span_processor
        
        # Install local queue processor (no auto-export)
        local_processor = LocalQueueSpanProcessor(self._local_queue)
        tracer_provider._active_span_processor = local_processor
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit context: Restore original processor, local queue dies.
        """
        # Restore original processor
        tracer_provider = trace.get_tracer_provider()
        tracer_provider._active_span_processor = self._original_processor
        
        # Local queue dies automatically with context
    
    def create_span(self, span_name: str, attributes: Dict[str, Any]) -> str:
        """
        Create span - goes to local queue, not global consumer queue.
        """
        tracer = trace.get_tracer("span_collector")
        with tracer.start_as_current_span(span_name) as span:
            span.set_attributes(attributes)
            # Span goes to local queue when context exits
        return span.get_span_context().span_id
    
    def get_all_spans(self) -> List[ReadableSpan]:
        """Get all spans from local queue."""
        return self._local_queue.copy()
    
    def export_spans(self) -> bool:
        """Export all spans from local queue as batch."""
        if not self._local_queue:
            return True
        
        result = self.exporter.export(self._local_queue)
        return result == SpanExportResult.SUCCESS

# In respan_tracing/core/client.py
class RespanClient:
    def get_span_collector(self, trace_id: str) -> SpanCollector:
        """
        Get context manager for local span collection.
        
        Example:
            from respan_tracing import get_client
            
            client = get_client()
            with client.get_span_collector("exp-123") as sc:
                sc.create_span("step1", {...})
                sc.create_span("step2", {...})
                
                # Optional: manual export
                sc.export_spans()
                
                # Or get spans for inspection
                all_spans = sc.get_all_spans()
            
            # sc dies automatically, memory safe
        """
        return SpanCollector(trace_id=trace_id, exporter=self._exporter)
```

### 2. **Disable Automatic Export Option**

**Add SDK Configuration:**

```python
# In respan_tracing/__init__.py

class RespanTelemetry:
    def __init__(
        self,
        app_name: str,
        custom_exporter: Optional[SpanExporter] = None,
        auto_export: bool = True,  # NEW: Control automatic export
        **kwargs
    ):
        """
        Args:
            auto_export: If False, spans are not automatically exported
                        on context exit. Use local variable collection for manual export.
        """
        if auto_export:
            # Use SimpleSpanProcessor (current behavior)
            processor = SimpleSpanProcessor(exporter)
        else:
            # Use NoOpSpanProcessor - no automatic export
            processor = NoOpSpanProcessor()
        
        # Store exporter for manual collection access
        self._exporter = custom_exporter or default_exporter
```

### 3. **Public Tracer API** ✅ **ALREADY IMPLEMENTED**

**Already available in RespanClient:**

```python
class RespanClient:
    def get_tracer(self):
        """
        Get the OpenTelemetry tracer for creating custom spans.
        
        Returns:
            opentelemetry.trace.Tracer: The OpenTelemetry tracer instance.
        """
        return self._tracer.get_tracer()
```

**Usage:**
```python
from respan_tracing import get_client

client = get_client()
tracer = client.get_tracer()

with tracer.start_as_current_span("my_operation") as span:
    span.set_attribute("custom.attribute", "value")
    # Your code here
```

**Status:** ✅ No changes needed - already part of the SDK API

---

## 🎯 Backend Usage Pattern (After SDK Enhancement)

### **New Context Manager + Local Queue Flow:**

```python
# In WorkflowExecutionTask.process_single_item()
from respan_tracing import get_client

# Phase 1: Execute workflows (no tracing context)
workflow_results = []
for workflow in workflows:
    if workflow_type == 'custom':
        # Custom workflows stay pending
        workflow_results.append(None)  # Placeholder
    else:
        # Execute hosted workflow
        result = executor.execute_workflow_only(workflow)  # No spans created
        workflow_results.append(result)

# Phase 2: Create trace from completed results (in ingest_workflow_output)
def ingest_workflow_output(workflow_result, trace_id, ...):
    from utils.telemetry.backend_exporter import set_telemetry_context
    
    # Set telemetry context
    set_telemetry_context(organization=org, experiment_id=exp_id)
    
    # Use context manager for local span collection (bypasses global consumer)
    client = get_client()
    with client.get_span_collector(trace_id) as sc:
        # Create spans - go to LOCAL queue, not global consumer queue
        sc.create_span(
            "workflow_execution", 
            attributes={
                "input": workflow_result["input"],
                "experiment_id": exp_id,
                "status": "completed"
            }
        )
        
        sc.create_span(
            f"{workflow_type}_step",
            attributes={
                "input": workflow_result["input"],
                "output": workflow_result["output"],
                "latency": workflow_result["metrics"]["latency"],
                "cost": workflow_result["metrics"]["cost"],
                "status": "completed"
            }
        )
        
        # Optional: inspect spans before export
        all_spans = sc.get_all_spans()
        print(f"Created {len(all_spans)} spans for trace {trace_id}")
        
        # Export entire trace as batch from local queue
        sc.export_spans()  # Single batch export
    
    # Context exits: sc dies automatically, local queue cleaned up
```

### **Benefits of This Approach:**

✅ **Bypasses Global Consumer**: Local queue prevents spans from auto-consuming  
✅ **Context Manager Safety**: Automatic cleanup when context exits  
✅ **Batch Ingestion Efficiency**: Single `log_dataset_request` call per trace  
✅ **No Memory Leaks**: Local queue dies with context automatically  
✅ **Inspection Capability**: `get_all_spans()` allows span inspection before export  
✅ **Custom Workflow Support**: Same pattern for hosted and custom workflows  
✅ **Centralized Control**: Manual export timing under user control

---

## 📋 Implementation Priority

### **Critical (Required for Backend):**
🚨 **SpanCollector context manager** - Local queue bypassing global consumer  
🚨 **get_span_collector() API** - Returns context manager for local collection  
🚨 **LocalQueueSpanProcessor** - Processor that routes to local queue instead of export  
🚨 **Processor swapping mechanism** - Temporarily replace global processor in context

### **Important (Better API):**
✅ ~~**get_tracer() public API**~~ - Already implemented in SDK

### **Nice to Have (Documentation):**
📝 **Updated examples** showing batch collection patterns  
📝 **Context variable patterns** for custom exporters  
📝 **SpanCollector usage guide** with memory safety best practices

---

## Summary

### **Current State:**
❌ SDK forces synchronous context management (automatic export on span exit)  
❌ Cannot batch spans by trace  
❌ Custom workflows cannot create spans asynchronously  

### **Required SDK Changes:**
🛠️ **SpanCollector context manager** - Local queue for manual span collection  
🛠️ **get_span_collector()** API - Returns context manager for batch collection  
🛠️ **LocalQueueSpanProcessor** - Processor that routes to local queue  
🛠️ **export_spans()** method - Batch export from local queue  
✅ ~~**get_tracer() public API**~~ - Already implemented

### **Backend Impact:**
🎯 **Enables asynchronous context management** for workflow system  
🎯 **Supports custom workflows** with same tracing pattern as hosted  
🎯 **Improves trace consistency** with batch export per trace  
🎯 **Matches customer flow** (execute → collect → export)

**Recommendation:** Implement SDK enhancements to enable asynchronous context management pattern required for consistent workflow tracing.

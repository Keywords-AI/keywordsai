# KeywordsAI Client API Guide

The KeywordsAI Client API provides a clean, intuitive way to interact with the current trace and span context. This replaces the need for the clumsy `@context.py` approach and provides automatic context-aware operations.

## Overview

The client API consists of:
- **`get_client()`** - Global function to get a client instance
- **`KeywordsAIClient`** - Main client class with trace operations
- **Automatic context detection** - No need to manually manage span references

## Quick Start

```python
from keywordsai_tracing import KeywordsAITelemetry, get_client, workflow

# Initialize telemetry (once per application)
telemetry = KeywordsAITelemetry(app_name="my-app")

@workflow(name="my_workflow")
def my_workflow():
    # Get client - works anywhere, no instance management needed
    client = get_client()
    
    # Get current trace information
    trace_id = client.get_current_trace_id()
    span_id = client.get_current_span_id()
    
    # Update current span with KeywordsAI parameters
    client.update_current_span(
        keywordsai_params={"trace_group_identifier": "my-group"},
        attributes={"custom.attribute": "value"}
    )
    
    return "success"
```

## API Reference

### Getting a Client

#### `get_client()` - Global Access
```python
from keywordsai_tracing import get_client

client = get_client()  # Returns singleton KeywordsAIClient instance
```

#### `telemetry.get_client()` - Instance Method
```python
telemetry = KeywordsAITelemetry()
client = telemetry.get_client()  # Returns new KeywordsAIClient instance
```

**Recommendation**: Use the global `get_client()` function for simplicity. It uses the same singleton tracer internally.

### Core Methods

#### Getting Current Trace Information

```python
client = get_client()

# Get current span object
span = client.get_current_span()  # Returns OpenTelemetry Span or None

# Get trace and span IDs as strings
trace_id = client.get_current_trace_id()  # Returns 32-char hex string or None
span_id = client.get_current_span_id()    # Returns 16-char hex string or None

# Check if currently recording
is_recording = client.is_recording()      # Returns bool
```

#### Updating Current Span

The `update_current_span()` method is the most powerful feature, allowing you to update multiple aspects of the current span in one call:

```python
success = client.update_current_span(
    # KeywordsAI-specific parameters (automatically validated)
    keywordsai_params={
        "trace_group_identifier": "my-group",
        "metadata": {
            "user_id": "123",
            "session_id": "abc"
        }
    },
    
    # Generic OpenTelemetry attributes
    attributes={
        "custom.attribute": "value",
        "processing.stage": "validation"
    },
    
    # Span status
    status=StatusCode.OK,  # or Status object
    status_description="Processing completed successfully",
    
    # Update span name
    name="updated_span_name"
)
```

#### Adding Events and Exceptions

```python
# Add events to track progress
client.add_event("processing_started", {
    "input_size": 1024,
    "timestamp": time.time()
})

# Record exceptions with automatic error status
try:
    risky_operation()
except Exception as e:
    client.record_exception(e, attributes={
        "error.context": "during_validation"
    })
    # Span status is automatically set to ERROR
```

#### Context Operations

```python
# Set values in OpenTelemetry context
client.set_context_value("session_id", "abc123")
client.set_context_value("user_id", 456)

# Get values from context
session_id = client.get_context_value("session_id")  # Returns "abc123"
user_id = client.get_context_value("user_id")        # Returns 456
missing = client.get_context_value("nonexistent")    # Returns None
```

## Usage Patterns

### 1. Simple Span Updates

Replace the old context manager approach:

```python
# OLD WAY (clumsy)
from keywordsai_tracing.contexts.span import keywordsai_span_attributes

@workflow(name="my_workflow")
def my_workflow():
    with keywordsai_span_attributes(
        keywordsai_params={"trace_group_identifier": "test"}
    ):
        # Your code here
        pass

# NEW WAY (clean)
@workflow(name="my_workflow") 
def my_workflow():
    client = get_client()
    client.update_current_span(
        keywordsai_params={"trace_group_identifier": "test"}
    )
    # Your code here - no context manager needed!
```

### 2. Progressive Span Enhancement

Build up span information as you go:

```python
@workflow(name="data_processing")
def process_data(data):
    client = get_client()
    
    # Initial setup
    client.update_current_span(
        keywordsai_params={"trace_group_identifier": "data-processing"},
        attributes={"input.size": len(data)}
    )
    
    # Validation phase
    client.add_event("validation_started")
    validated_data = validate(data)
    client.update_current_span(
        attributes={"validation.result": "success"}
    )
    
    # Processing phase  
    client.add_event("processing_started")
    result = process(validated_data)
    client.update_current_span(
        attributes={
            "processing.result": "success",
            "output.size": len(result)
        },
        status=StatusCode.OK
    )
    
    return result
```

### 3. Error Handling

Comprehensive error tracking:

```python
@task(name="risky_operation")
def risky_operation(data):
    client = get_client()
    
    try:
        client.add_event("operation_started", {"input": str(data)})
        
        if not data:
            raise ValueError("Empty data provided")
            
        result = complex_processing(data)
        
        client.update_current_span(
            attributes={"operation.result": "success"},
            status=StatusCode.OK
        )
        
        return result
        
    except ValueError as e:
        # Record exception with context
        client.record_exception(e, attributes={
            "error.type": "validation_error",
            "error.input": str(data)
        })
        
        # Add additional context
        client.update_current_span(
            attributes={"operation.result": "failed"}
        )
        
        raise  # Re-raise for caller
```

### 4. Cross-Function Trace Tracking

Track trace information across function calls:

```python
@workflow(name="multi_step_workflow")
def multi_step_workflow():
    client = get_client()
    
    # Get trace ID for logging/correlation
    trace_id = client.get_current_trace_id()
    logger.info(f"Starting workflow {trace_id}")
    
    # Set workflow-level context
    client.set_context_value("workflow_start_time", time.time())
    
    step1_result = step1()
    step2_result = step2(step1_result)
    step3_result = step3(step2_result)
    
    # Calculate total time using context
    start_time = client.get_context_value("workflow_start_time")
    total_time = time.time() - start_time
    
    client.update_current_span(
        attributes={"workflow.total_time": total_time}
    )
    
    return step3_result

def step1():
    client = get_client()
    # Same trace context is automatically available
    trace_id = client.get_current_trace_id()  # Same as workflow
    # ... processing
    
def step2(data):
    client = get_client()
    # Context values are also available
    start_time = client.get_context_value("workflow_start_time")
    # ... processing
```

## Best Practices

### 1. Use Global `get_client()`
```python
# ✅ GOOD - Simple and clean
client = get_client()

# ❌ AVOID - Unnecessary complexity
telemetry = KeywordsAITelemetry()
client = telemetry.get_client()
```

### 2. Update Spans Progressively
```python
# ✅ GOOD - Build up information as you go
client.update_current_span(attributes={"stage": "validation"})
# ... do validation
client.update_current_span(attributes={"validation.result": "success"})
# ... do processing  
client.update_current_span(attributes={"stage": "processing"})

# ❌ AVOID - Setting everything at once at the end
# (loses the progressive tracking benefit)
```

### 3. Always Check Return Values for Critical Operations
```python
# ✅ GOOD - Check if operations succeeded
success = client.update_current_span(critical_attributes)
if not success:
    logger.warning("Failed to update span with critical attributes")

# ✅ ALSO GOOD - For non-critical operations, you can ignore
client.add_event("debug_checkpoint")  # Don't need to check
```

### 4. Use Structured Attribute Names
```python
# ✅ GOOD - Structured naming
client.update_current_span(attributes={
    "user.id": user_id,
    "user.role": user_role,
    "request.method": "POST",
    "request.path": "/api/data"
})

# ❌ AVOID - Flat naming
client.update_current_span(attributes={
    "userid": user_id,
    "userrole": user_role,
    "method": "POST",
    "path": "/api/data"
})
```

## Migration from Old Context Manager

If you're currently using the `keywordsai_span_attributes` context manager, here's how to migrate:

### Before (Context Manager)
```python
from keywordsai_tracing.contexts.span import keywordsai_span_attributes

@workflow(name="my_workflow")
def my_workflow():
    with keywordsai_span_attributes(
        keywordsai_params={
            "trace_group_identifier": "my-group",
            "metadata": {"user_id": "123"}
        }
    ):
        result = do_processing()
        return result
```

### After (Client API)
```python
from keywordsai_tracing import get_client

@workflow(name="my_workflow")
def my_workflow():
    client = get_client()
    client.update_current_span(
        keywordsai_params={
            "trace_group_identifier": "my-group", 
            "metadata": {"user_id": "123"}
        }
    )
    
    result = do_processing()
    return result
```

### Benefits of Migration
- **No context manager nesting** - Cleaner code structure
- **Progressive updates** - Add information as you go
- **Better error handling** - Return values indicate success/failure
- **More functionality** - Events, exceptions, status updates
- **Easier testing** - No context manager setup required

## Error Handling

The client API is designed to be robust and never crash your application:

```python
client = get_client()

# All methods return success indicators or safe defaults
span = client.get_current_span()          # Returns None if no span
trace_id = client.get_current_trace_id()  # Returns None if no span
success = client.update_current_span()    # Returns False if failed
success = client.add_event("test")        # Returns False if failed

# Methods log warnings for debugging but don't raise exceptions
# Check logs if operations aren't working as expected
```

## Thread Safety

The client API is thread-safe and works correctly in multi-threaded environments:

- **Singleton client** - Same instance across threads
- **Context propagation** - OpenTelemetry context flows across threads
- **Thread-local spans** - Each thread has its own active span context

```python
import threading
from keywordsai_tracing import get_client

def worker_function(worker_id):
    client = get_client()  # Same client instance
    
    # But each thread has its own span context
    trace_id = client.get_current_trace_id()  # Different per thread
    client.update_current_span(
        attributes={"worker.id": worker_id}
    )

# This works correctly
threads = []
for i in range(5):
    t = threading.Thread(target=worker_function, args=(i,))
    threads.append(t)
    t.start()
```

## Summary

The KeywordsAI Client API provides:

1. **Simple access** - `get_client()` works anywhere
2. **Automatic context** - No manual span management
3. **Comprehensive functionality** - Get info, update spans, handle errors
4. **Clean migration path** - Easy upgrade from context managers
5. **Robust error handling** - Never crashes your application
6. **Thread safety** - Works in multi-threaded environments

This replaces the old clumsy context manager approach with a clean, intuitive API that automatically works with the current trace context. 
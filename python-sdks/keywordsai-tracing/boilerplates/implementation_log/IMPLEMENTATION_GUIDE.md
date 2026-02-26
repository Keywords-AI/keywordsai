# Respan OpenTelemetry Implementation Guide

This document explains the new direct OpenTelemetry implementation that replaces the Traceloop SDK dependency.

## 🎯 Overview

The new implementation provides the same functionality as Traceloop but with direct OpenTelemetry usage, offering better control, performance, and maintainability.

## 🏗️ Architecture

### Core Components

```
src/respan_tracing/
├── core/                    # Core OpenTelemetry implementation
│   ├── tracer.py           # Main tracer class (replaces Traceloop)
│   ├── processor.py        # Custom span processor for metadata
│   └── exporter.py         # Respan-specific OTLP exporter
├── decorators/             # Function/class decorators
│   ├── base.py            # Base decorator implementation
│   └── __init__.py        # Workflow, task, agent, tool decorators
├── contexts/              # Context managers
│   └── span.py           # Span attribute context manager
├── utils/                 # Utility functions
│   ├── notebook.py       # Notebook detection
│   └── instrumentation.py # Library instrumentation
├── instruments.py         # Instrumentation enum
└── main.py               # Main RespanTelemetry class
```

## 🔄 Migration from Traceloop

### Before (with Traceloop)
```python
from respan_tracing import RespanTelemetry
from traceloop.sdk import Traceloop

# Traceloop was initialized internally
k_tl = RespanTelemetry()
```

### After (Direct OpenTelemetry)
```python
from respan_tracing import RespanTelemetry

# Same interface, but now uses direct OpenTelemetry
k_tl = RespanTelemetry()
```

**No code changes required!** The API remains the same.

## 🧵 Threading and Concurrency

### How Traceloop Handled Threading
- Used `ThreadingInstrumentor().instrument()` for context propagation
- Singleton pattern with thread-safe initialization
- BatchSpanProcessor for production, SimpleSpanProcessor for notebooks

### Our Implementation
```python
class RespanTracer:
    _instance = None
    _lock = Lock()
    
    def __new__(cls, *args, **kwargs):
        """Thread-safe singleton pattern"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def _setup_threading(self):
        """Setup threading instrumentation for context propagation"""
        ThreadingInstrumentor().instrument()
```

### Key Threading Features
1. **Thread-safe singleton**: Only one tracer instance across all threads
2. **Context propagation**: OpenTelemetry context flows across thread boundaries
3. **Batch processing**: Background thread handles span export without blocking
4. **Graceful shutdown**: Proper cleanup on application exit

## 📊 Span Processing Pipeline

### 1. Span Creation
```python
def _setup_span(entity_name: str, span_kind: str, version: Optional[int] = None):
    """Setup OpenTelemetry span and context"""
    tracer = RespanTracer().get_tracer()
    span = tracer.start_span(f"{entity_name}.{span_kind}")
    
    # Set Respan-specific attributes
    span.set_attribute(SpanAttributes.TRACELOOP_SPAN_KIND, tlp_span_kind.value)
    span.set_attribute(SpanAttributes.TRACELOOP_ENTITY_NAME, entity_name)
```

### 2. Metadata Injection
```python
class RespanSpanProcessor:
    def on_start(self, span, parent_context):
        """Add Respan metadata to spans"""
        # Add workflow name, entity path, trace group ID, etc.
        workflow_name = context_api.get_value("respan_workflow_name")
        if workflow_name:
            span.set_attribute(SpanAttributes.TRACELOOP_WORKFLOW_NAME, workflow_name)
```

### 3. Export to Respan
```python
class RespanSpanExporter:
    def __init__(self, endpoint, api_key, headers):
        # Build proper OTLP endpoint
        traces_endpoint = self._build_traces_endpoint(endpoint)
        
        # Initialize OTLP exporter with auth
        self.exporter = OTLPSpanExporter(
            endpoint=traces_endpoint,
            headers={"Authorization": f"Bearer {api_key}", **headers}
        )
```

## 🎛️ Instrumentation Management

### Dynamic Library Detection
```python
def _init_openai() -> bool:
    """Initialize OpenAI instrumentation"""
    if not is_package_installed("openai"):
        return False
    
    try:
        from opentelemetry.instrumentation.openai import OpenAIInstrumentor
        instrumentor = OpenAIInstrumentor()
        if not instrumentor.is_instrumented_by_opentelemetry:
            instrumentor.instrument()
        return True
    except Exception as e:
        logging.error(f"Failed to initialize OpenAI instrumentation: {e}")
        return False
```

### Supported Libraries
- **AI/ML**: OpenAI, Anthropic, Cohere, Mistral, Ollama, Groq, etc.
- **Cloud AI**: AWS Bedrock, Google Vertex AI, IBM Watson X
- **Vector DBs**: Pinecone, Qdrant, Chroma, Milvus, Weaviate
- **Frameworks**: LangChain, LlamaIndex, Haystack, CrewAI
- **Infrastructure**: Redis, Requests, urllib3, PyMySQL

## 🎨 Decorator Implementation

### Unified Async/Sync Support
```python
def _create_entity_method_decorator(name, version, span_kind):
    def decorator(fn):
        if _is_async_method(fn):
            if inspect.isasyncgenfunction(fn):
                # Handle async generators
                @wraps(fn)
                async def async_gen_wrapper(*args, **kwargs):
                    span, ctx_token = _setup_span(entity_name, span_kind, version)
                    try:
                        result = fn(*args, **kwargs)
                        async for item in _ahandle_generator(span, ctx_token, result):
                            yield item
                    except Exception as e:
                        span.record_exception(e)
                        raise
                return async_gen_wrapper
            else:
                # Handle regular async functions
                @wraps(fn)
                async def async_wrapper(*args, **kwargs):
                    span, ctx_token = _setup_span(entity_name, span_kind, version)
                    try:
                        result = await fn(*args, **kwargs)
                        return result
                    finally:
                        _cleanup_span(span, ctx_token)
                return async_wrapper
        else:
            # Handle sync functions and generators
            @wraps(fn)
            def sync_wrapper(*args, **kwargs):
                span, ctx_token = _setup_span(entity_name, span_kind, version)
                try:
                    result = fn(*args, **kwargs)
                    if inspect.isgeneratorfunction(fn):
                        return _handle_generator(span, ctx_token, result)
                    else:
                        return result
                finally:
                    if not inspect.isgeneratorfunction(fn):
                        _cleanup_span(span, ctx_token)
            return sync_wrapper
    return decorator
```

## 🔧 Configuration Options

### Environment Variables
```bash
RESPAN_API_KEY=your-api-key
RESPAN_BASE_URL=https://api.respan.ai/api
RESPAN_DISABLE_BATCH=false
```

### Programmatic Configuration
```python
from respan_tracing import RespanTelemetry, Instruments

telemetry = RespanTelemetry(
    app_name="my-app",
    api_key="your-key",
    base_url="https://api.respan.ai/api",
    disable_batch=False,
    instruments={Instruments.OPENAI, Instruments.ANTHROPIC},
    block_instruments={Instruments.REDIS, Instruments.REQUESTS},
    resource_attributes={"service.version": "1.0.0"},
    enabled=True
)
```

## 🚀 Performance Improvements

### 1. Reduced Dependencies
- **Before**: Traceloop SDK + its dependencies
- **After**: Direct OpenTelemetry (already required)

### 2. Better Batch Processing
```python
# Choose processor based on environment
if disable_batch or is_notebook():
    processor = SimpleSpanProcessor(exporter)  # Immediate export
else:
    processor = BatchSpanProcessor(exporter)   # Batched export
```

### 3. Efficient Context Management
```python
@contextmanager
def respan_span_attributes(**kwargs):
    """Efficient context value management"""
    tokens = []
    for key, value in context_values.items():
        token = context_api.attach(context_api.set_value(key, value))
        tokens.append(token)
    
    try:
        yield
    finally:
        for token in reversed(tokens):
            context_api.detach(token)
```

## 🧪 Testing

Run the test script to verify the implementation:

```bash
python test_new_implementation.py
```

### Test Coverage
- ✅ Basic initialization
- ✅ Workflow and task decorators
- ✅ Context manager functionality
- ✅ Async/await support
- ✅ Error handling and exception recording
- ✅ Mock library integration

## 🔍 Debugging

### Enable Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Now you'll see detailed OpenTelemetry logs
telemetry = RespanTelemetry()
```

### Verify Spans are Created
```python
from opentelemetry import trace

@workflow(name="debug_workflow")
def debug_workflow():
    current_span = trace.get_current_span()
    print(f"Current span: {current_span}")
    print(f"Span context: {current_span.get_span_context()}")
```

## 📈 Benefits Over Traceloop

1. **Direct Control**: No wrapper layer, direct OpenTelemetry usage
2. **Better Performance**: Reduced overhead, optimized batch processing
3. **Cleaner Dependencies**: Fewer external dependencies
4. **Enhanced Debugging**: Better error messages and logging
5. **Future-Proof**: Direct OpenTelemetry ensures compatibility
6. **Thread Safety**: Improved concurrent execution handling
7. **Async Support**: Native async/await and generator support

## 🔄 Backward Compatibility

The new implementation maintains 100% API compatibility:

```python
# All existing code continues to work unchanged
from respan_tracing import RespanTelemetry, workflow, task
from respan_tracing.contexts.span import respan_span_attributes

k_tl = RespanTelemetry()

@workflow(name="my_workflow")
def my_workflow():
    with respan_span_attributes(
        respan_params={"trace_group_identifier": "test"}
    ):
        # Your existing code here
        pass
```

## 🎯 Next Steps

1. **Test thoroughly** with your existing codebase
2. **Monitor performance** improvements
3. **Remove Traceloop dependency** from requirements
4. **Update documentation** to reflect the new implementation
5. **Consider additional OpenTelemetry features** now available

The new implementation provides a solid foundation for future enhancements while maintaining the familiar Respan API. 
# OTEL Compliance Implementation Notes

## What We Built

An OTEL-compliant instrumentation package for Langfuse that redirects traces to Keywords AI.

## The Standard Pattern (Industrial Standard)

Based on OpenTelemetry Python documentation and existing instrumentors like `RequestsInstrumentor`, `FlaskInstrumentor`, etc.

### Usage Pattern

```python
# 1. Import the instrumentor class
from opentelemetry.instrumentation.requests import RequestsInstrumentor

# 2. Call .instrument() BEFORE importing target library
RequestsInstrumentor().instrument()

# 3. Now use the library normally
import requests
requests.get("https://example.com")  # Automatically traced
```

### Why Instrument Before Import?

Monkey-patching must happen before the target library creates instances. Otherwise, already-loaded references won't be patched.

## Our Implementation

### Architecture

```
LangfuseInstrumentor (extends BaseInstrumentor)
  └─ .instrument() 
       └─ Uses wrapt.wrap_function_wrapper()
            └─ Patches httpx.Client.send()
                 └─ Intercepts /api/public/ingestion requests
                      └─ Transforms Langfuse format → Keywords AI format
                           └─ Redirects to Keywords AI API
```

### Key OTEL Compliance Points

1. **Uses BaseInstrumentor** - Standard OTEL pattern
2. **Uses wrapt** - Safe, reversible monkey-patching
3. **Single responsibility** - Only patches HTTP client, doesn't create span processors
4. **No import substitution** - Users use `from langfuse import Langfuse` normally
5. **Entry points** - Supports `opentelemetry-instrument` auto-instrumentation
6. **Instrumentation before import** - Follows standard OTEL order

### What We DON'T Do (Avoiding Mistakes)

- ❌ Create custom SpanProcessor (that's for span export, not instrumentation)
- ❌ Monkey-patch OTEL exporter globally
- ❌ Force import substitution
- ❌ Mix instrumentation with export concerns

## Why Previous Implementation Was Wrong

The old approach:
1. Monkey-patched `OTLPSpanExporter.export` globally (wrong layer)
2. Created custom `SpanProcessor` (mixing concerns)
3. Required import substitution (not OTEL standard)

The issue: Instrumentation packages should ONLY patch the target library, not create exporters or processors.

## Langfuse Architecture (What We're Patching)

Langfuse SDK:
- Uses `@observe()` decorator to collect spans
- Batches observations
- Sends via `httpx.Client` to Langfuse backend at `/api/public/ingestion`

Our patch:
- Intercepts the HTTP request
- Transforms the batch payload
- Redirects to Keywords AI

## References

- OTEL Instrumentation Docs: https://opentelemetry.io/docs/languages/python/libraries/
- BaseInstrumentor: https://opentelemetry-python-contrib.readthedocs.io/en/latest/instrumentation/base/instrumentor.html
- wrapt library: https://wrapt.readthedocs.io/

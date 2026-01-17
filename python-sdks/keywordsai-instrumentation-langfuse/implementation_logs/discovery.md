# Discovery: Langfuse v3 Uses OTLP Exporter

## What We Found

Running the test revealed that Langfuse v3:
1. **Uses OTLP HTTP exporter** - sends to `/api/public/otel/v1/traces`
2. **Uses urllib3/requests** - NOT httpx
3. **Sends OTEL spans** - in protobuf or JSON format

Evidence:
```
urllib3.connectionpool - DEBUG - https://cloud.langfuse.com:443 "POST /api/public/otel/v1/traces HTTP/1.1" 401
opentelemetry.exporter.otlp.proto.http.trace_exporter - ERROR - Failed to export span batch code: 401
```

## What This Means

Our current implementation is WRONG because:
1. We're patching `httpx.Client.send()` but Langfuse uses `urllib3`
2. We're expecting Langfuse batch format but it sends OTEL spans
3. We need the transformation from `deprecated_exporter.py` after all!

## The Correct Approach

We need to patch the **OTLP exporter** itself, which is exactly what deprecated_exporter did!

Options:
1. **Patch OTLPSpanExporter** (what deprecated_exporter did)
   - Pros: Catches all OTEL spans from Langfuse
   - Cons: Monkey-patches OTEL internals (less clean)

2. **Patch urllib3 or requests**
   - Pros: More general HTTP interception
   - Cons: Messier, harder to target only Langfuse requests

3. **Use SpanProcessor** (what I mistakenly thought was wrong)
   - Pros: Proper OTEL pattern for intercepting spans
   - Cons: You said "instrumentation shouldn't create processors"
   
## Resolution Needed

The deprecated_exporter approach (patching OTLPSpanExporter) might actually be the right approach for Langfuse v3!

But we should do it via `BaseInstrumentor` + `wrapt` to make it OTEL-compliant.

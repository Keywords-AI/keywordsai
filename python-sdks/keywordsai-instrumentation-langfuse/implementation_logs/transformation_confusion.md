# Transformation Format Confusion

## The Problem

There are TWO different data formats to handle:

### 1. OTEL Spans (from deprecated_exporter.py)
- **Source**: OpenTelemetry SDK's `OTLPSpanExporter`
- **Format**: OTEL Span objects with attributes like:
  - `span.context.trace_id`
  - `span.context.span_id`
  - `span.attributes["langfuse.observation.type"]`
  - `span.start_time` (nanoseconds)
  - etc.

### 2. Langfuse HTTP Batch Format (what I assumed)
- **Source**: Langfuse SDK's HTTP client sending to `/api/public/ingestion`
- **Format**: JSON batch with events like:
  ```json
  {
    "batch": [
      {
        "type": "observation-create",
        "body": {
          "id": "...",
          "traceId": "...",
          "name": "...",
          "type": "generation",
          "input": {...},
          "output": {...}
        }
      }
    ]
  }
  ```

## The Question

**Which format does Langfuse v3 actually send via httpx?**

### Scenario A: Langfuse sends OTEL spans via HTTP
- Then we need the transformation from `deprecated_exporter.py`
- We patch httpx and transform OTEL spans → Keywords AI format

### Scenario B: Langfuse sends its own format
- Then we need my simpler transformation
- We patch httpx and transform Langfuse batch → Keywords AI format

## The Answer

Need to check Langfuse v3 source code or test what it actually sends.

If Langfuse v3 is truly OTEL-based, it might:
1. Create OTEL spans internally
2. Use OTLPSpanExporter to send them
3. Send to `/api/public/otel` endpoint (OTLP format)

OR it might:
1. Create OTEL spans internally  
2. Convert to Langfuse format
3. Send to `/api/public/ingestion` endpoint (Langfuse format)

## Resolution Needed

User is pointing out that the deprecated_exporter transformation is more complete.
We need to figure out which transformation to use!

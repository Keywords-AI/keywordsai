# Keywords AI LiteLLM Exporter

LiteLLM callback integration that exports traces to Keywords AI.

## Installation

```bash
pip install keywordsai-exporter-litellm
```

## Quick Start

### Method 1: Callback

LiteLLM-native callback integration:

```python
import litellm
from keywordsai_exporter_litellm import KeywordsAILiteLLMCallback

callback = KeywordsAILiteLLMCallback(api_key="your-api-key")
litellm.success_callback = [callback.log_success_event]
litellm.failure_callback = [callback.log_failure_event]

response = litellm.completion(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

### Method 2: Proxy

Route requests through Keywords AI's API:

```python
import litellm

litellm.api_base = "https://api.keywordsai.co/api/"

response = litellm.completion(
    api_key="your-keywordsai-api-key",
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

## Creating Trace Hierarchies

Pass trace IDs via `keywordsai_params`:

```python
import uuid
import time
from datetime import datetime, timezone
import litellm
from keywordsai_exporter_litellm import KeywordsAILiteLLMCallback

callback = KeywordsAILiteLLMCallback(api_key="your-api-key")
litellm.success_callback = [callback.log_success_event]

# Generate trace identifiers
trace_id = uuid.uuid4().hex
workflow_span_id = uuid.uuid4().hex[:16]
workflow_start = datetime.now(timezone.utc)

# Make LLM calls with shared trace_id
response1 = litellm.completion(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Step 1"}],
    metadata={
        "keywordsai_params": {
            "trace_id": trace_id,
            "parent_span_id": workflow_span_id,
            "span_name": "step_1",
        }
    }
)

response2 = litellm.completion(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Step 2"}],
    metadata={
        "keywordsai_params": {
            "trace_id": trace_id,
            "parent_span_id": workflow_span_id,
            "span_name": "step_2",
        }
    }
)

# Send the workflow span last
time.sleep(1.0)  # Wait for generation spans to be sent
callback.send_workflow_span(
    trace_id=trace_id,
    span_id=workflow_span_id,
    workflow_name="my_workflow",
    start_time=workflow_start,
    end_time=datetime.now(timezone.utc),
)
```

## Custom Parameters

Pass Keywords AI parameters via metadata:

```python
response = litellm.completion(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello!"}],
    metadata={
        "keywordsai_params": {
            "customer_identifier": "user-123",
            "thread_identifier": "thread-456",
            "workflow_name": "my_workflow",
            "metadata": {"custom_key": "custom_value"},
        }
    }
)
```

## Streaming & Async Support

```python
# Streaming
response = litellm.completion(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello!"}],
    stream=True
)
for chunk in response:
    print(chunk.choices[0].delta.content or "", end="")

# Async
response = await litellm.acompletion(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

## Tool Calls

Tool/function calls are automatically captured:

```python
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get the current weather",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string"}
            },
            "required": ["location"]
        }
    }
}]

response = litellm.completion(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "What's the weather in NYC?"}],
    tools=tools,
    tool_choice="auto"
)
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `KEYWORDSAI_API_KEY` | Your Keywords AI API key | Required |
| `KEYWORDSAI_ENDPOINT` | Custom endpoint | `https://api.keywordsai.co/api/v1/traces/ingest` |

## API Reference

### KeywordsAILiteLLMCallback

```python
from keywordsai_exporter_litellm import KeywordsAILiteLLMCallback

callback = KeywordsAILiteLLMCallback(
    api_key="...",    # Keywords AI API key
    endpoint="...",   # Custom endpoint (optional)
    timeout=10,       # Request timeout in seconds
)

# Register callbacks
litellm.success_callback = [callback.log_success_event]
litellm.failure_callback = [callback.log_failure_event]

# Send workflow span for trace hierarchy
callback.send_workflow_span(
    trace_id="...",           # Unique trace ID
    span_id="...",            # Unique span ID
    workflow_name="...",      # Workflow name
    start_time=datetime,      # Start time
    end_time=datetime,        # End time
    customer_identifier="...", # Customer ID (optional)
    metadata={},              # Additional metadata (optional)
)
```

## License

MIT

# Keywords AI LiteLLM Exporter

LiteLLM integration for exporting traces to Keywords AI.

## Installation

```bash
pip install keywordsai-exporter-litellm
```

## Quick Start

### Callback Mode

Use the callback to send traces to Keywords AI:

```python
import litellm
from keywordsai_exporter_litellm import KeywordsAILiteLLMCallback

# Setup callback
callback = KeywordsAILiteLLMCallback(api_key="your-keywordsai-api-key")
callback.register_litellm_callbacks()

# Make LLM calls - traces are automatically sent
response = litellm.completion(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello!"}],
)
```

### Proxy Mode

Route requests through Keywords AI gateway:

```python
import litellm

response = litellm.completion(
    api_key="your-keywordsai-api-key",
    api_base="https://api.keywordsai.co/api",
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello!"}],
)
```

## Creating Traces

### Callback Mode (with `keywordsai_params`)

```python
import uuid
import litellm
from keywordsai_exporter_litellm import KeywordsAILiteLLMCallback

callback = KeywordsAILiteLLMCallback(api_key="your-api-key")
callback.register_litellm_callbacks()

trace_id = uuid.uuid4().hex
root_span_id = uuid.uuid4().hex[:16]
child_span_id = uuid.uuid4().hex[:16]

# Root span
response1 = litellm.completion(
    api_key="your-api-key",
    api_base="https://api.keywordsai.co/api",
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello!"}],
    metadata={
        "keywordsai_params": {
            "trace_id": trace_id,
            "span_id": root_span_id,
            "workflow_name": "my_workflow",
            "span_name": "root_generation",
            "customer_identifier": "user-123",
        }
    },
)

# Child span
response2 = litellm.completion(
    api_key="your-api-key",
    api_base="https://api.keywordsai.co/api",
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Follow up!"}],
    metadata={
        "keywordsai_params": {
            "trace_id": trace_id,
            "span_id": child_span_id,
            "parent_span_id": root_span_id,
            "workflow_name": "my_workflow",
            "span_name": "child_generation",
            "customer_identifier": "user-123",
        }
    },
)
```

### Proxy Mode (with `extra_body`)

```python
import uuid
import litellm

trace_id = uuid.uuid4().hex
root_span_id = uuid.uuid4().hex[:16]
child_span_id = uuid.uuid4().hex[:16]

# Root span
response1 = litellm.completion(
    api_key="your-keywordsai-api-key",
    api_base="https://api.keywordsai.co/api",
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello!"}],
    extra_body={
        "trace_unique_id": trace_id,
        "span_unique_id": root_span_id,
        "span_workflow_name": "my_workflow",
        "span_name": "root_generation",
        "customer_identifier": "user-123",
    },
)

# Child span
response2 = litellm.completion(
    api_key="your-keywordsai-api-key",
    api_base="https://api.keywordsai.co/api",
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Follow up!"}],
    extra_body={
        "trace_unique_id": trace_id,
        "span_unique_id": child_span_id,
        "span_parent_id": root_span_id,
        "span_workflow_name": "my_workflow",
        "span_name": "child_generation",
        "customer_identifier": "user-123",
    },
)
```

## Parameters

### Callback Mode (`keywordsai_params`)

| Parameter | Description |
|-----------|-------------|
| `trace_id` | Unique trace identifier |
| `span_id` | Unique span identifier |
| `parent_span_id` | Parent span ID (for nested spans) |
| `workflow_name` | Workflow/trace name |
| `span_name` | Span name |
| `customer_identifier` | Customer identifier |
| `thread_identifier` | Thread identifier |
| `metadata` | Additional metadata dict |

### Proxy Mode (`extra_body`)

| Parameter | Description |
|-----------|-------------|
| `trace_unique_id` | Unique trace identifier |
| `span_unique_id` | Unique span identifier |
| `span_parent_id` | Parent span ID (for nested spans) |
| `span_workflow_name` | Workflow/trace name |
| `span_name` | Span name |
| `customer_identifier` | Customer identifier |

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `KEYWORDSAI_API_KEY` | Keywords AI API key | Required |
| `KEYWORDSAI_ENDPOINT` | Traces endpoint (callback mode) | `https://api.keywordsai.co/api/v1/traces/ingest` |

## License

MIT

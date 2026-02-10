# Respan LiteLLM Exporter

LiteLLM integration for exporting logs and traces to Respan.

## Installation

```bash
pip install respan-exporter-litellm
```

## Quick Start

### Callback Mode

Use the callback to send traces to Respan:

```python
import litellm
from respan_exporter_litellm import RespanLiteLLMCallback

# Setup callback
callback = RespanLiteLLMCallback(api_key="your-respan-api-key")
callback.register_litellm_callbacks()

# Make LLM calls - traces are automatically sent
response = litellm.completion(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello!"}],
)
```

### Proxy Mode

Route requests through Respan gateway:

```python
import litellm

response = litellm.completion(
    api_key="your-respan-api-key",
    api_base="https://api.respan.ai/api",
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello!"}],
)
```

## Logging

If you just want individual logs (no trace/span IDs), omit trace fields and
send only basic metadata. This will produce one log per request.

### Callback Mode (with `respan_params`)

```python
import litellm
from respan_exporter_litellm import RespanLiteLLMCallback

callback = RespanLiteLLMCallback(api_key="your-api-key")
callback.register_litellm_callbacks()

response = litellm.completion(
    api_key="your-api-key",
    api_base="https://api.respan.ai/api",
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello!"}],
    metadata={
        "respan_params": {
            "workflow_name": "simple_logging",
            "span_name": "single_log",
            "customer_identifier": "user-123",
        }
    },
)
```

### Proxy Mode (with `extra_body`)

```python
import litellm

response = litellm.completion(
    api_key="your-respan-api-key",
    api_base="https://api.respan.ai/api",
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello!"}],
    extra_body={
        "span_workflow_name": "simple_logging",
        "span_name": "single_log",
        "customer_identifier": "user-123",
    },
)
```

## License

MIT

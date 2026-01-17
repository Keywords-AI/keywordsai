# 🗝️ Keywords AI LiteLLM Exporter

OpenTelemetry-compliant instrumentation for LiteLLM that exports traces to the Keywords AI platform.

## Installation

```bash
pip install keywordsai-exporter-litellm
```

## Usage

### Method 1: Using the Instrumentor (Recommended)

The `LiteLLMInstrumentor` provides full OpenTelemetry-compliant instrumentation using wrapt patching:

```python
import os
from keywordsai_exporter_litellm import LiteLLMInstrumentor

# Set your API key
os.environ["KEYWORDSAI_API_KEY"] = "your-api-key"

# Instrument LiteLLM
LiteLLMInstrumentor().instrument()

# Now use LiteLLM normally - all calls are traced and exported to Keywords AI!
import litellm

response = litellm.completion(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

You can also pass the API key directly:

```python
LiteLLMInstrumentor().instrument(
    api_key="your-api-key",
    endpoint="https://api.keywordsai.co/api/v1/traces/ingest",  # optional
    service_name="my-llm-service"  # optional
)
```

To disable instrumentation:

```python
LiteLLMInstrumentor().uninstrument()
```

### Method 2: Using the Callback

The `KeywordsAILiteLLMCallback` integrates with LiteLLM's native callback system:

```python
import os
import litellm
from keywordsai_exporter_litellm import KeywordsAILiteLLMCallback

# Set your API key
os.environ["KEYWORDSAI_API_KEY"] = "your-api-key"

# Create callback instance
callback = KeywordsAILiteLLMCallback()

# Register with LiteLLM's success and failure callbacks
# Note: Pass the bound methods, not the class instance
litellm.success_callback = [callback.log_success_event]
litellm.failure_callback = [callback.log_failure_event]

# Make completion calls
response = litellm.completion(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

### Method 3: Using Keywords AI as a Proxy

Alternatively, you can route requests through Keywords AI's API:

```python
import os
import litellm

# Set Keywords AI as the API base
litellm.api_base = "https://api.keywordsai.co/api/"
KEYWORDSAI_API_KEY = os.getenv("KEYWORDSAI_API_KEY")

response = litellm.completion(
    api_key=KEYWORDSAI_API_KEY,  # Use Keywords AI API key
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello!"}]
)

# View logs at https://platform.keywordsai.co/
```

## Passing Custom Parameters

You can pass additional Keywords AI parameters via metadata:

```python
response = litellm.completion(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello!"}],
    metadata={
        "keywordsai_params": {
            "customer_params": {
                "customer_identifier": "user-123",
                "email": "user@example.com",
                "name": "John Doe"
            },
            "thread_identifier": "thread-456",
            "metadata": {"custom_key": "custom_value"},
            "evaluation_identifier": "eval-789",
            "prompt_id": "prompt-abc",
        }
    }
)
```

## Streaming Support

Both the Instrumentor and Callback support streaming responses:

```python
response = litellm.completion(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello!"}],
    stream=True
)

for chunk in response:
    print(chunk.choices[0].delta.content or "", end="")
```

## Async Support

Async completions are fully supported:

```python
import asyncio
import litellm

async def main():
    response = await litellm.acompletion(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Hello!"}]
    )
    print(response)

asyncio.run(main())
```

## Tool Calls Support

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
                "location": {"type": "string", "description": "City name"}
            },
            "required": ["location"]
        }
    }
}]

response = litellm.completion(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "What's the weather in NYC?"}],
    tools=tools,
    tool_choice="auto"
)
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `KEYWORDSAI_API_KEY` | Your Keywords AI API key | Required |
| `KEYWORDSAI_ENDPOINT` | Custom Keywords AI endpoint | `https://api.keywordsai.co/api/v1/traces/ingest` |

## API Reference

### LiteLLMInstrumentor

```python
class LiteLLMInstrumentor(BaseInstrumentor):
    def instrument(
        self,
        api_key: str = None,           # Keywords AI API key
        endpoint: str = None,          # Custom endpoint
        service_name: str = None,      # Service name for traces
        tracer_provider: TracerProvider = None  # Custom tracer provider
    ) -> None: ...
    
    def uninstrument(self) -> None: ...
```

### KeywordsAILiteLLMCallback

```python
class KeywordsAILiteLLMCallback:
    def __init__(
        self,
        api_key: str = None,    # Keywords AI API key
        endpoint: str = None,   # Custom endpoint
        timeout: int = 10       # Request timeout in seconds
    ): ...
```

## License

MIT

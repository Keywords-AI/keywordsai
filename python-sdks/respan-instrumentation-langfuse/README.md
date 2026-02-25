# Respan Instrumentation for Langfuse

**[respan.ai](https://respan.ai)** | **[Documentation](https://docs.respan.ai)** | **[PyPI](https://pypi.org/project/respan-instrumentation-langfuse/)**

**OTEL-compliant** automatic instrumentation for Langfuse to send traces to Respan.

## ✅ Why This Implementation is OTEL-Compliant

This package follows OpenTelemetry best practices:

- ✅ **Uses `BaseInstrumentor`** - Standard OTEL instrumentation interface
- ✅ **Uses `wrapt` for safe patching** - Reliable, reversible monkey-patching of httpx.Client  
- ✅ **Single responsibility** - Only does instrumentation (HTTP interception), not span processing
- ✅ **No import substitution** - Use `from langfuse import Langfuse` normally!
- ✅ **Minimal interception** - Only redirects Langfuse's HTTP requests to Respan
- ✅ **Supports uninstrumentation** - Can be cleanly enabled/disabled
- ✅ **Compatible with auto-instrumentation** - Works with `opentelemetry-instrument`

## Installation

```bash
pip install respan-instrumentation-langfuse
```

## Usage

### Option 1: Standard OTEL Pattern (Recommended)

```python
# IMPORTANT: Instrument BEFORE importing Langfuse
from respan_instrumentation_langfuse import LangfuseInstrumentor

LangfuseInstrumentor().instrument(api_key="your-respan-api-key")

# Now import and use Langfuse normally - NO code changes needed!
from langfuse import Langfuse, observe

langfuse = Langfuse(
    public_key="your-langfuse-public-key",
    secret_key="your-langfuse-secret-key",
)

@observe()
def my_llm_function(query: str):
    # Your LLM code here
    return f"Response to: {query}"

# All traces automatically go to Respan!
result = my_llm_function("Hello!")
langfuse.flush()
```

### Option 2: Using Environment Variables

```bash
export RESPAN_API_KEY="your-api-key"
# Optionally set custom endpoint:
# export RESPAN_ENDPOINT="https://custom.endpoint.com/api/v1/traces/ingest"

# Langfuse credentials (Langfuse SDK's own env vars):
export LANGFUSE_PUBLIC_KEY="your-langfuse-public-key"
export LANGFUSE_SECRET_KEY="your-langfuse-secret-key"
```

```python
# Instrument before importing Langfuse
from respan_instrumentation_langfuse import LangfuseInstrumentor
LangfuseInstrumentor().instrument()

# Use Langfuse normally
from langfuse import Langfuse, observe
```

### Option 3: Zero-Code Auto-Instrumentation

If you have `opentelemetry-instrument` configured:

```bash
export RESPAN_API_KEY="your-api-key"
# Langfuse credentials can be set via Langfuse's own env vars:
export LANGFUSE_PUBLIC_KEY="your-langfuse-public-key"
export LANGFUSE_SECRET_KEY="your-langfuse-secret-key"

opentelemetry-instrument python your_app.py
```

**Note:** `LANGFUSE_PUBLIC_KEY` and `LANGFUSE_SECRET_KEY` are Langfuse SDK's own environment variables, not specific to this instrumentation package.

## How It Works

The instrumentor patches Langfuse's HTTP client to redirect trace data from Langfuse backend to Respan:

1. You call `LangfuseInstrumentor().instrument()` before importing Langfuse
2. This patches `httpx.Client.send()` using `wrapt` (safe, reversible)
3. You use Langfuse normally with `@observe()` decorators
4. When Langfuse sends data to its backend, the patch intercepts the HTTP request
5. Data is transformed from Langfuse format to Respan format
6. Request is redirected to Respan API instead

**Why patch before import?** The HTTP client must be patched before Langfuse creates its client instances. This is standard OTEL instrumentation behavior.


## Configuration

### Environment Variables

- `RESPAN_API_KEY` - Your Respan API key (required)
- `RESPAN_ENDPOINT` - Custom endpoint URL (optional, defaults to `https://api.respan.ai/api/v1/traces/ingest`)

### Programmatic Configuration

```python
from respan_instrumentation_langfuse import instrument

instrument(
    api_key="your-api-key",
    endpoint="https://custom-endpoint.com/api/v1/traces/ingest",
)
```

## Advanced Usage

### Custom Endpoint

```python
from respan_instrumentation_langfuse import LangfuseInstrumentor

LangfuseInstrumentor().instrument(
    api_key="your-api-key",
    endpoint="https://your-instance.com/api/v1/traces/ingest"
)

from langfuse import Langfuse, observe
```

### Disabling Instrumentation

```python
from respan_instrumentation_langfuse import LangfuseInstrumentor

instrumentor = LangfuseInstrumentor()
instrumentor.instrument(api_key="your-key")

# ... use Langfuse ...

# Disable when done
instrumentor.uninstrument()
```

## Troubleshooting

### Spans Not Appearing in Respan

1. Check your API key is set correctly
2. Ensure `langfuse.flush()` is called before program exit
3. Check logs for any error messages
4. Verify network connectivity to Respan API

### Import Errors

Make sure all dependencies are installed:

```bash
pip install opentelemetry-api opentelemetry-sdk opentelemetry-instrumentation wrapt langfuse requests
```

### Compatibility Issues

- Requires Python 3.8+
- Requires Langfuse SDK v2.0.0+
- Requires OpenTelemetry SDK v1.20.0+

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/

# Lint
ruff check src/
```

## What Makes This OTEL-Compliant?

1. **Uses `BaseInstrumentor`** - Standard OTEL pattern with `.instrument()` and `.uninstrument()`
2. **Uses `wrapt` for Patching** - Safe, reversible monkey-patching of httpx client
3. **Single Responsibility** - Only intercepts HTTP requests, doesn't create custom span processors
4. **No Import Substitution** - Use `from langfuse import Langfuse` normally
5. **Entry Points** - Supports `opentelemetry-instrument` auto-instrumentation

## License

Apache 2.0

## Support

- Documentation: https://docs.respan.ai
- Issues: https://github.com/Repsan/respan/issues
- Email: support@respan.ai

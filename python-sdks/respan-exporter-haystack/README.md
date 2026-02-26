# Respan Haystack Integration

**[respan.ai](https://respan.ai)** | **[Documentation](https://docs.respan.ai)** | **[PyPI](https://pypi.org/project/respan-exporter-haystack/)**

Respan integration for Haystack pipelines with tracing and logging support.

## Features

### Gateway Mode
Route LLM calls through Respan gateway:
- Automatic logging (zero config)
- Model fallbacks & retries
- Load balancing
- Cost optimization
- Rate limiting & caching

### Tracing Mode
Capture full workflow execution:
- Multi-component pipelines
- Parent-child span relationships
- Timing per component
- Input/output tracking
- RAG + Agent workflows

### Combined Mode (Recommended)
Use both together for:
- Gateway reliability + Tracing visibility
- Production-ready monitoring

---

## Installation

```bash
pip install respan-exporter-haystack
```

## Quick Start

### 1. Get API Keys

- [Respan API Key](https://platform.respan.co/)
- OpenAI API Key (for examples)

### 2. Set Environment Variables

```bash
export RESPAN_API_KEY="your-respan-key"
export OPENAI_API_KEY="your-openai-key"
export HAYSTACK_CONTENT_TRACING_ENABLED="true"  # For tracing mode
```

---

## Usage Examples

### Gateway Mode (Auto-Logging)

**Just replace `OpenAIGenerator` with `RespanGenerator`:**

```python
import os
from haystack import Pipeline
from haystack.components.builders import PromptBuilder
from respan_exporter_haystack.gateway import RespanGenerator

# Create pipeline
pipeline = Pipeline()
pipeline.add_component(
    name="prompt",
    instance=PromptBuilder(template="Tell me about {{topic}}."),
)
pipeline.add_component(
    name="llm",
    instance=RespanGenerator(
    model="gpt-4o-mini",
    api_key=os.getenv("RESPAN_API_KEY")
),
)
pipeline.connect(sender="prompt", receiver="llm")

# Run
result = pipeline.run({"prompt": {"topic": "machine learning"}})
print(result["llm"]["replies"][0])
```

**That's it!** All LLM calls are automatically logged to Respan with no additional code.

**See:** [`examples/gateway_example.py`](examples/gateway_example.py)

---

### Prompt Management

**Use platform-managed prompts** for centralized control:

```python
import os
from haystack import Pipeline
from respan_exporter_haystack.gateway import RespanGenerator

# Create prompt on platform: https://platform.respan.co/platform/prompts
# Get your prompt_id from the platform

# Create pipeline with platform prompt (model config comes from platform)
pipeline = Pipeline()
pipeline.add_component(
    name="llm",
    instance=RespanGenerator(
    prompt_id="1210b368ce2f4e5599d307bc591d9b7a",  # Your prompt ID
    api_key=os.getenv("RESPAN_API_KEY")
),
)

# Run with prompt variables
result = pipeline.run({
    "llm": {
        "prompt_variables": {
            "user_input": "The cat sat on the mat"
        }
    }
})

print("Response received successfully!")
print(f"Model: {result['llm']['meta'][0]['model']}")
print(f"Tokens: {result['llm']['meta'][0]['usage']['total_tokens']}")
```

**Benefits:**
- Update prompts without code changes
- Model config managed on platform (no hardcoding)
- Version control & rollback
- A/B testing
- Team collaboration

**See:** [`examples/prompt_example.py`](examples/prompt_example.py)

---

### Tracing Mode (Workflow Monitoring)

**Add `RespanConnector` to capture the entire pipeline:**

```python
import os
from haystack import Pipeline
from haystack.components.builders import PromptBuilder
from haystack.components.generators import OpenAIGenerator
from respan_exporter_haystack.connector import RespanConnector

os.environ["HAYSTACK_CONTENT_TRACING_ENABLED"] = "true"

# Create pipeline with tracing
pipeline = Pipeline()
pipeline.add_component(name="tracer", instance=RespanConnector(name="My Workflow"))
pipeline.add_component(
    name="prompt",
    instance=PromptBuilder(template="Tell me about {{topic}}."),
)
pipeline.add_component(name="llm", instance=OpenAIGenerator(model="gpt-4o-mini"))
pipeline.connect(sender="prompt", receiver="llm")

# Run
result = pipeline.run({"prompt": {"topic": "artificial intelligence"}})
print(result["llm"]["replies"][0])
print(f"\nTrace URL: {result['tracer']['trace_url']}")

```

**Dashboard shows:**
- Pipeline (root span)
- PromptBuilder (template processing)
- LLM (generation with tokens + cost)

**See:** [`examples/tracing_example.py`](examples/tracing_example.py)

---

### Combined Mode (Recommended for Production)

**Use BOTH gateway + prompt + tracing for the full stack:**

```python
import os
from haystack import Pipeline
from respan_exporter_haystack.connector import RespanConnector
from respan_exporter_haystack.gateway import RespanGenerator

os.environ["HAYSTACK_CONTENT_TRACING_ENABLED"] = "true"

# Create pipeline with gateway, prompt management, and tracing
pipeline = Pipeline()
pipeline.add_component(
    name="tracer",
    instance=RespanConnector(name="Full Stack: Gateway + Prompt + Tracing"),
)
pipeline.add_component(
    name="llm",
    instance=RespanGenerator(
    prompt_id="1210b368ce2f4e5599d307bc591d9b7a",  # Platform-managed prompt
    api_key=os.getenv("RESPAN_API_KEY")
),
)

# Run with prompt variables
result = pipeline.run({
    "llm": {
        "prompt_variables": {
            "user_input": "She sells seashells by the seashore"
        }
    }
})

print("Response received successfully!")
print(f"Trace URL: {result['tracer']['trace_url']}")
```

**You get:**
1. **Gateway routing** with fallbacks, cost tracking, and reliability
2. **Platform prompts** managed centrally (no hardcoded prompts/models)
3. **Full workflow trace** with all components and timing

**See:** [`examples/combined_example.py`](examples/combined_example.py)

---

## What Gets Logged

### Gateway Mode
- Model used
- Prompt & completion
- Tokens & cost
- Latency
- Request metadata

### Tracing Mode
Each span includes:
- Component name & type
- Input data
- Output data
- Timing (latency)
- Parent-child relationships

For LLM spans, additionally:
- Model name
- Token counts
- Calculated cost (auto-computed)

---

## View Your Data

All logs and traces appear in your Respan dashboard:

**Dashboard:** https://platform.respan.co/logs

- **Logs view:** Individual LLM calls
- **Traces view:** Full pipeline workflows with tree visualization

---

## API Reference

### `RespanGenerator`

Gateway component for LLM calls.

```python
RespanGenerator(
    model: Optional[str] = None,         # Model name (e.g., "gpt-4o-mini") - optional if using prompt_id
    api_key: Optional[str] = None,       # API key (defaults to RESPAN_API_KEY)
    base_url: Optional[str] = None,      # API base URL (defaults to https://api.respan.ai)
    prompt_id: Optional[str] = None,     # Platform prompt ID for prompt management
    generation_kwargs: Optional[Dict] = None
)
```

**Replaces:** `OpenAIGenerator` with gateway routing

**Note:** When using `prompt_id`, model config comes from the platform - no need to specify `model`

---

### `RespanConnector`

Tracing component for workflow monitoring.

```python
RespanConnector(
    name: str,                           # Pipeline name for dashboard
    api_key: Optional[str] = None,       # API key (defaults to RESPAN_API_KEY)
    base_url: Optional[str] = None,      # API base URL (defaults to https://api.respan.ai/api)
    metadata: Optional[Dict] = None      # Custom metadata for all spans
)
```

**Returns:** `{"name": str, "trace_url": str}`

**Requires:** `HAYSTACK_CONTENT_TRACING_ENABLED=true` environment variable

---

## Examples

Run the examples:

```bash
# Set environment variables
export RESPAN_API_KEY="your-key"
export OPENAI_API_KEY="your-openai-key"
export HAYSTACK_CONTENT_TRACING_ENABLED="true"

# Gateway mode (auto-logging)
python examples/gateway_example.py

# Tracing mode (workflow monitoring)
python examples/tracing_example.py

# Prompt management (platform prompts)
python examples/prompt_example.py

# Combined mode (gateway + prompt + tracing)
python examples/combined_example.py
```

---

## Requirements

- Python 3.9+
- `haystack-ai >= 2.0.0`
- `requests >= 2.31.0`

---

## Support

- **Documentation:** https://docs.respan.ai/
- **Dashboard:** https://platform.respan.ai/
- **Issues:** [GitHub Issues](https://github.com/respan-ai/respan-sdks/issues)

---

## License

MIT License - see [LICENSE](LICENSE) file for details.

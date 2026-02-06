# Keywords AI Haystack Integration

Monitor and optimize your Haystack pipelines with Keywords AI's LLM observability platform.

## Features

### Gateway Mode
Route LLM calls through Keywords AI gateway:
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
pip install keywordsai-exporter-haystack
```

## Quick Start

### 1. Get API Keys

- [Keywords AI API Key](https://platform.keywordsai.co/)
- OpenAI API Key (for examples)

### 2. Set Environment Variables

```bash
export KEYWORDSAI_API_KEY="your-keywords-ai-key"
export OPENAI_API_KEY="your-openai-key"
export HAYSTACK_CONTENT_TRACING_ENABLED="true"  # For tracing mode
```

---

## Usage Examples

### Gateway Mode (Auto-Logging)

**Just replace `OpenAIGenerator` with `KeywordsAIGenerator`:**

```python
import os
from haystack import Pipeline
from haystack.components.builders import PromptBuilder
from keywordsai_exporter_haystack import KeywordsAIGenerator

# Create pipeline
pipeline = Pipeline()
pipeline.add_component("prompt", PromptBuilder(template="Tell me about {{topic}}."))
pipeline.add_component("llm", KeywordsAIGenerator(
    model="gpt-4o-mini",
    api_key=os.getenv("KEYWORDSAI_API_KEY")
))
pipeline.connect("prompt", "llm")

# Run
result = pipeline.run({"prompt": {"topic": "machine learning"}})
print(result["llm"]["replies"][0])
```

**That's it!** All LLM calls are automatically logged to Keywords AI with no additional code.

**See:** [`examples/gateway_example.py`](examples/gateway_example.py)

---

### Prompt Management

**Use platform-managed prompts** for centralized control:

```python
import os
from haystack import Pipeline
from keywordsai_exporter_haystack import KeywordsAIGenerator

# Create prompt on platform: https://platform.keywordsai.co/platform/prompts
# Get your prompt_id from the platform

# Create pipeline with platform prompt (model config comes from platform)
pipeline = Pipeline()
pipeline.add_component("llm", KeywordsAIGenerator(
    prompt_id="1210b368ce2f4e5599d307bc591d9b7a",  # Your prompt ID
    api_key=os.getenv("KEYWORDSAI_API_KEY")
))

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

**Add `KeywordsAIConnector` to capture the entire pipeline:**

```python
import os
from haystack import Pipeline
from haystack.components.builders import PromptBuilder
from haystack.components.generators import OpenAIGenerator
from keywordsai_exporter_haystack import KeywordsAIConnector

os.environ["HAYSTACK_CONTENT_TRACING_ENABLED"] = "true"

# Create pipeline with tracing
pipeline = Pipeline()
pipeline.add_component("tracer", KeywordsAIConnector("My Workflow"))
pipeline.add_component("prompt", PromptBuilder(template="Tell me about {{topic}}."))
pipeline.add_component("llm", OpenAIGenerator(model="gpt-4o-mini"))
pipeline.connect("prompt", "llm")

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
from keywordsai_exporter_haystack import KeywordsAIConnector, KeywordsAIGenerator

os.environ["HAYSTACK_CONTENT_TRACING_ENABLED"] = "true"

# Create pipeline with gateway, prompt management, and tracing
pipeline = Pipeline()
pipeline.add_component("tracer", KeywordsAIConnector("Full Stack: Gateway + Prompt + Tracing"))
pipeline.add_component("llm", KeywordsAIGenerator(
    prompt_id="1210b368ce2f4e5599d307bc591d9b7a",  # Platform-managed prompt
    api_key=os.getenv("KEYWORDSAI_API_KEY")
))

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

All logs and traces appear in your Keywords AI dashboard:

**Dashboard:** https://platform.keywordsai.co/logs

- **Logs view:** Individual LLM calls
- **Traces view:** Full pipeline workflows with tree visualization

---

## API Reference

### `KeywordsAIGenerator`

Gateway component for LLM calls.

```python
KeywordsAIGenerator(
    model: Optional[str] = None,         # Model name (e.g., "gpt-4o-mini") - optional if using prompt_id
    api_key: Optional[str] = None,       # Keywords AI API key (defaults to KEYWORDSAI_API_KEY env var)
    base_url: Optional[str] = None,      # API base URL (defaults to https://api.keywordsai.co)
    prompt_id: Optional[str] = None,     # Platform prompt ID for prompt management
    generation_kwargs: Optional[Dict] = None
)
```

**Replaces:** `OpenAIGenerator` with gateway routing

**Note:** When using `prompt_id`, model config comes from the platform - no need to specify `model`

---

### `KeywordsAIConnector`

Tracing component for workflow monitoring.

```python
KeywordsAIConnector(
    name: str,                           # Pipeline name for dashboard
    api_key: Optional[str] = None,       # Keywords AI API key (defaults to KEYWORDSAI_API_KEY env var)
    base_url: Optional[str] = None,      # API base URL (defaults to https://api.keywordsai.co)
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
export KEYWORDSAI_API_KEY="your-key"
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

- **Documentation:** https://docs.keywordsai.co/
- **Dashboard:** https://platform.keywordsai.co/
- **Issues:** [GitHub Issues](https://github.com/Keywords-AI/keywordai_sdks/issues)

---

## License

MIT License - see [LICENSE](LICENSE) file for details.

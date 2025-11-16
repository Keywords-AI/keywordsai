# Building an LLM Workflow with KeywordsAI Tracing

This tutorial demonstrates how to build and trace complex LLM workflows using KeywordsAI Tracing. We'll create an example that generates jokes, translates them to pirate language, and simulates audience reactions - all while capturing detailed telemetry of our LLM calls.

## Prerequisites

- Python 3.7+
- OpenAI API key
- Anthropic API key
- Keywords AI API key, you can get your API key from the [API keys page](https://platform.keywordsai.co/platform/api/api-keys)

## Installation
```bash
pip install keywordsai-tracing openai anthropic
```

## Initialization

### KeywordsAITelemetry Configuration

The `KeywordsAITelemetry` class is the main entry point for the SDK. Initialize it once at application startup:

```python
from keywordsai_tracing import KeywordsAITelemetry

telemetry = KeywordsAITelemetry(
    app_name="my-app",
    api_key="kwai-xxx",  # Or set KEYWORDSAI_API_KEY env var
)
```

### All Initialization Parameters

```python
KeywordsAITelemetry(
    # Basic Configuration
    app_name: str = "keywordsai",              # Application name for telemetry
    api_key: Optional[str] = None,             # API key (or KEYWORDSAI_API_KEY env var)
    base_url: Optional[str] = None,            # API URL (or KEYWORDSAI_BASE_URL env var)
    
    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO",
    
    # Performance
    is_batching_enabled: Optional[bool] = None,  # Enable background batch processing (default: True)
    
    # Instrumentation (see Instrumentation section below)
    instruments: Optional[Set[Instruments]] = None,        # Specific instruments to enable
    block_instruments: Optional[Set[Instruments]] = None,  # Instruments to disable
    
    # Advanced
    headers: Optional[Dict[str, str]] = None,              # Additional HTTP headers
    resource_attributes: Optional[Dict[str, str]] = None,  # Resource attributes
    span_postprocess_callback: Optional[Callable] = None,  # Span processing callback
    is_enabled: bool = True,                               # Enable/disable telemetry
    custom_exporter: Optional[SpanExporter] = None,        # Custom span exporter
)
```

### Parameter Reference

#### **Basic Configuration**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `app_name` | `str` | `"keywordsai"` | Name of your application for telemetry identification |
| `api_key` | `str \| None` | `None` | KeywordsAI API key. Can also be set via `KEYWORDSAI_API_KEY` environment variable |
| `base_url` | `str \| None` | `None` | KeywordsAI API base URL. Can also be set via `KEYWORDSAI_BASE_URL` environment variable. Defaults to `https://api.keywordsai.co/api` |

#### **Logging**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `log_level` | `str` | `"INFO"` | Logging level for KeywordsAI tracing. Options: `"DEBUG"`, `"INFO"`, `"WARNING"`, `"ERROR"`, `"CRITICAL"`. Can also be set via `KEYWORDSAI_LOG_LEVEL` environment variable |

#### **Performance**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `is_batching_enabled` | `bool \| None` | `None` | Enable batch span processing. When `False`, uses synchronous export (no background threads). Defaults to `True`. Useful to disable for debugging or backends with custom exporters. Can also be set via `KEYWORDSAI_BATCHING_ENABLED` environment variable |

#### **Instrumentation**

See [Instrumentation section](#instrumentation) for detailed information.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `instruments` | `Set[Instruments] \| None` | `None` | Specific instruments to enable. If `None`, enables all available instruments. Use empty set `set()` to disable all auto-instrumentation |
| `block_instruments` | `Set[Instruments] \| None` | `None` | Instruments to explicitly disable. Use this to block specific instrumentations while enabling others |

**Examples:**

```python
# Enable only specific instruments
from keywordsai_tracing import Instruments

telemetry = KeywordsAITelemetry(
    instruments={Instruments.OPENAI, Instruments.ANTHROPIC}
)

# Block specific instruments
telemetry = KeywordsAITelemetry(
    block_instruments={Instruments.REQUESTS, Instruments.URLLIB3}
)

# Disable all auto-instrumentation
telemetry = KeywordsAITelemetry(
    instruments=set()  # Empty set = no auto-instrumentation
)
```

#### **Advanced**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `headers` | `Dict[str, str] \| None` | `None` | Additional HTTP headers to send with telemetry data |
| `resource_attributes` | `Dict[str, str] \| None` | `None` | Additional resource attributes to attach to all spans. Useful for adding environment, version, etc. |
| `span_postprocess_callback` | `Callable \| None` | `None` | Optional callback function to process spans before export. Signature: `callback(span: ReadableSpan) -> None` |
| `is_enabled` | `bool` | `True` | Enable or disable telemetry. When `False`, becomes a no-op (no spans created) |
| `custom_exporter` | `SpanExporter \| None` | `None` | Custom span exporter to use instead of the default HTTP OTLP exporter. When provided, `api_key` and `base_url` are not required. See [Custom Exporters section](#custom-exporters) |

**Note:** Threading instrumentation is ALWAYS enabled by default (even when specifying custom instruments) because it's critical for context propagation. To disable it explicitly, use `block_instruments={Instruments.THREADING}`. See [Threading Instrumentation](#important-threading-instrumentation) for details.

### Common Configuration Patterns

#### **Development (Full Visibility)**

```python
telemetry = KeywordsAITelemetry(
    app_name="my-app-dev",
    api_key="kwai-xxx",
    log_level="DEBUG",  # Verbose logging
    # All instruments enabled by default
)
```

#### **Production (Optimized)**

```python
telemetry = KeywordsAITelemetry(
    app_name="my-app-prod",
    api_key="kwai-xxx",
    log_level="WARNING",  # Less verbose
    block_instruments={
        Instruments.REQUESTS,  # Reduce noise
        Instruments.URLLIB3,
    }
)
```

#### **Backend with Custom Logging (Minimal)**

```python
from your_exporters import DirectLoggingExporter

telemetry = KeywordsAITelemetry(
    app_name="my-backend",
    custom_exporter=DirectLoggingExporter(),  # Custom exporter
    is_batching_enabled=False,  # No background threads
    instruments=set(),  # No auto-instrumentation
    block_instruments={Instruments.THREADING},  # Disable threading if single-threaded
)
```

#### **Testing/Disabled**

```python
telemetry = KeywordsAITelemetry(
    app_name="my-app-test",
    is_enabled=False,  # Completely disabled (no-op)
)
```

### Environment Variables

You can configure KeywordsAI tracing using environment variables:

| Environment Variable | Description | Default |
|---------------------|-------------|---------|
| `KEYWORDSAI_API_KEY` | API key | None |
| `KEYWORDSAI_BASE_URL` | API base URL | `https://api.keywordsai.co/api` |
| `KEYWORDSAI_LOG_LEVEL` | Logging level | `INFO` |
| `KEYWORDSAI_BATCHING_ENABLED` | Enable batch processing | `True` |

**Example:**

```bash
export KEYWORDSAI_API_KEY="kwai-xxx"
export KEYWORDSAI_LOG_LEVEL="DEBUG"
export KEYWORDSAI_BATCHING_ENABLED="false"
```

```python
# No need to pass parameters - read from env vars
telemetry = KeywordsAITelemetry(app_name="my-app")
```

## Tutorial

### Step 1: Initialization
```
import os
from keywordsai_tracing.main import KeywordsAITelemetry
from keywordsai_tracing.decorators import workflow, task
import time

# Initialize KeywordsAI Telemetry
os.environ["KEYWORDSAI_API_KEY"] = "YOUR_KEYWORDSAI_API_KEY"
k_tl = KeywordsAITelemetry()

# Initialize OpenAI client
from openai import OpenAI
client = OpenAI()
```


### Step 2: First Draft - Basic Workflow
We'll start by creating a simple workflow that generates a joke, translates it to pirate speak,
and adds a signature. This demonstrates the basic usage of tasks and workflows.

- A task is a single unit of work, decorated with `@task`
- A workflow is a collection of tasks, decorated with `@workflow`
- Tasks can be used independently or as part of workflows

```python
@task(name="joke_creation")
def create_joke():
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Tell me a joke about opentelemetry"}],
        temperature=0.5,
        max_tokens=100,
        frequency_penalty=0.5,
        presence_penalty=0.5,
        stop=["\n"],
        logprobs=True,
    )
    return completion.choices[0].message.content

@task(name="signature_generation")
def generate_signature(joke: str):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": "add a signature to the joke:\n\n" + joke}
        ],
    )
    return completion.choices[0].message.content

@task(name="pirate_joke_translation")
def translate_joke_to_pirate(joke: str):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": "translate the joke to pirate language:\n\n" + joke,
            }
        ],
    )
    return completion.choices[0].message.content

@workflow(name="pirate_joke_generator")
def joke_workflow():
    eng_joke = create_joke()
    pirate_joke = translate_joke_to_pirate(eng_joke)
    signature = generate_signature(pirate_joke)
    return pirate_joke + signature

if __name__ == "__main__":
    joke_workflow()
```

Run the workflow and see the trace in Keywords AI `Traces` tab.

### Step 3: Adding Another Workflow
Let's add audience reactions to make our workflow more complex and demonstrate
what multiple workflow traces look like.

```python
@task(name="audience_laughs")
def audience_laughs(joke: str):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": "This joke:\n\n" + joke + " is funny, say hahahahaha",
            }
        ],
        max_tokens=10,
    )
    return completion.choices[0].message.content

@task(name="audience_claps")
def audience_claps():
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Clap once"}],
        max_tokens=5,
    )
    return completion.choices[0].message.content

@task(name="audience_applaud")
def audience_applaud(joke: str):
    clap = audience_claps()
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": "Applaud to the joke, clap clap! " + clap,
            }
        ],
        max_tokens=10,
    )
    return completion.choices[0].message.content

@workflow(name="audience_reaction")
def audience_reaction(joke: str):
    laughter = audience_laughs(joke=joke)
    applauds = audience_applaud(joke=joke)
    return laughter + applauds


@workflow(name="joke_and_audience_reaction") #<--------- Create the new workflow that combines both workflows together
def joke_and_audience_reaction():
    pirate_joke = joke_workflow()
    reactions = audience_reaction(pirate_joke)
```

Don't forget to update the entrypoint!
```python
if __name__ == "__main__":
    joke_and_audience_reaction() # <--------- Update the entrypoint here
```

Run the workflow again and see the trace in Keywords AI `Traces` tab, notice the new span for the `audience_reaction` workflow in parallel with the `joke_workflow`. Congratulation! You have created a trace with multiple workflows.

### Step 4: Adding Vector Storage Capability
To demonstrate how to integrate with vector databases and embeddings,
we'll add a store_joke task that generates embeddings for our jokes.

```python
@task(name="store_joke")
def store_joke(joke: str):
    """Simulate storing a joke in a vector database."""
    embedding = client.embeddings.create(
        model="text-embedding-3-small",
        input=joke,
    )
    return embedding.data[0].embedding
```

Update create_joke to use store_joke
```python
@task(name="joke_creation")
def create_joke():
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Tell me a joke about opentelemetry"}],
        temperature=0.5,
        max_tokens=100,
        frequency_penalty=0.5,
        presence_penalty=0.5,
        stop=["\n"],
        logprobs=True,
    )
    joke = completion.choices[0].message.content
    store_joke(joke)  # <--------- Add the task here
    return joke
```
Run the workflow again and see the trace in Keywords AI `Traces` tab, notice the new span for the `store_joke` task.

Expanding the `store_joke` task, you can see the embeddings call is recognized as `openai.embeddings`.

### Step 5: Adding Arbitrary Function Calls
Demonstrate how to trace non-LLM functions by adding a logging task.

```python
@task(name="logging_joke")
def logging_joke(joke: str, reactions: str):
    """Simulates logging the process into a database."""
    print(joke + "\n\n" + reactions)
    time.sleep(1)
```

Update `joke_and_audience_reaction`
```python
@workflow(name="joke_and_audience_reaction")
def joke_and_audience_reaction():
    pirate_joke = joke_workflow()
    reactions = audience_reaction(pirate_joke)
    logging_joke(pirate_joke, reactions) # <-------- Add this workflow here
```

Run the workflow again and see the trace in Keywords AI `Traces` tab, notice the new span for the `logging_joke` task.

This is a simple example of how to trace arbitrary functions. You can see the all the inputs and outputs of `logging_joke` task.

### Step 6: Adding Different LLM Provider (Anthropic)

Demonstrate compatibility with multiple LLM providers by adding Anthropic integration.

```python
from anthropic import Anthropic
anthropic = Anthropic()

@task(name="ask_for_comments")
def ask_for_comments(joke: str):
    completion = anthropic.messages.create(
        model="claude-3-5-sonnet-20240620",
        messages=[{"role": "user", "content": f"What do you think about this joke: {joke}"}],
        max_tokens=100,
    )
    return completion.content[0].text

@task(name="read_joke_comments")
def read_joke_comments(comments: str):
    return f"Here is the comment from the audience: {comments}"

@workflow(name="audience_interaction")
def audience_interaction(joke: str):
    comments = ask_for_comments(joke=joke)
    read_joke_comments(comments=comments)
```

Update `joke_and_audience_reaction`
```python
@workflow(name="joke_and_audience_reaction")
def joke_and_audience_reaction():
    pirate_joke = joke_workflow()
    reactions = audience_reaction(pirate_joke)
    audience_interaction(pirate_joke) # <-------- Add this workflow here
    logging_joke(pirate_joke, reactions)
```

Running the workflow for one last time, you can see that the new `audience_interaction` can recognize the `anthropic.completion` calls.

## Instrumentation

### What is Instrumentation?

Instrumentation is the process of automatically adding telemetry (traces/spans) to library calls without modifying your code. When you enable instrumentation for a library (like OpenAI, Anthropic, LangChain), the SDK automatically captures:

- LLM requests and responses
- Model parameters (temperature, max_tokens, etc.)
- Token usage and costs
- Latency and timing
- Errors and exceptions

### Default Behavior: All Instrumentations Enabled

**By default, KeywordsAI tracing attempts to enable ALL available instrumentations.**

```python
from keywordsai_tracing import KeywordsAITelemetry

# This enables ALL available instrumentations (if packages are installed)
telemetry = KeywordsAITelemetry(
    app_name="my-app",
    api_key="kwai-xxx"
)
```

If a library is installed in your environment, its instrumentation will be automatically enabled. If not installed, it's silently skipped (no errors).

### Available Instrumentations

The SDK supports instrumentation for:

**AI/ML Libraries:**
- `openai` - OpenAI API
- `anthropic` - Anthropic (Claude) API
- `cohere` - Cohere API
- `mistral` - Mistral AI
- `ollama` - Ollama (local models)
- `groq` - Groq API
- `together` - Together AI
- `replicate` - Replicate
- `transformers` - Hugging Face Transformers

**Cloud AI Services:**
- `bedrock` - AWS Bedrock
- `sagemaker` - AWS SageMaker
- `vertexai` - Google Vertex AI
- `google_generativeai` - Google AI (Gemini)
- `watsonx` - IBM WatsonX
- `alephalpha` - Aleph Alpha

**Vector Databases:**
- `pinecone` - Pinecone
- `qdrant` - Qdrant
- `chroma` - Chroma
- `milvus` - Milvus
- `weaviate` - Weaviate
- `lancedb` - LanceDB
- `marqo` - Marqo

**Frameworks:**
- `langchain` - LangChain
- `llama_index` - LlamaIndex
- `haystack` - Haystack
- `crew` - CrewAI
- `mcp` - Model Context Protocol

**Infrastructure:**
- `redis` - Redis
- `requests` - HTTP requests library
- `urllib3` - urllib3 HTTP client
- `pymysql` - PyMySQL database client
- `threading` - Context propagation across threads (⚠️ **Always enabled by default**)

### Installing Instrumentation Packages

**Important:** To trace a specific library, you need to install the corresponding OpenTelemetry instrumentation package.

The SDK uses the **OpenTelemetry standard** instrumentation packages:

```bash
# Install instrumentation for the libraries you use
pip install opentelemetry-instrumentation-openai
pip install opentelemetry-instrumentation-anthropic
pip install opentelemetry-instrumentation-langchain
pip install opentelemetry-instrumentation-requests
```

**Naming convention:** `opentelemetry-instrumentation-<library-name>`

#### Example: Tracing OpenAI Calls

```bash
# 1. Install OpenAI client
pip install openai

# 2. Install OpenTelemetry instrumentation for OpenAI
pip install opentelemetry-instrumentation-openai

# 3. Install KeywordsAI tracing
pip install keywordsai-tracing
```

```python
from keywordsai_tracing import KeywordsAITelemetry
from openai import OpenAI

# Initialize telemetry (OpenAI instrumentation auto-enabled)
telemetry = KeywordsAITelemetry(
    app_name="my-app",
    api_key="kwai-xxx"
)

client = OpenAI()

# This call is automatically traced!
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

The OpenAI call will automatically create a span with:
- Model name
- Prompt and completion
- Token usage
- Latency
- Cost (if available)

### Important: Threading Instrumentation

**Threading instrumentation is automatically enabled** (even when you specify custom instruments) because it's critical for context propagation across threads.

```python
# These all include threading by default:
telemetry = KeywordsAITelemetry()  # All instruments including threading

telemetry = KeywordsAITelemetry(
    instruments={Instruments.OPENAI}  # OpenAI + Threading (auto-added!)
)

telemetry = KeywordsAITelemetry(
    instruments={Instruments.OPENAI, Instruments.ANTHROPIC}  # + Threading!
)
```

**To disable threading** (if you're certain your app is single-threaded):

```python
telemetry = KeywordsAITelemetry(
    block_instruments={Instruments.THREADING}  # Explicitly disabled
)
```

### Controlling Instrumentation

#### Option 1: Disable Specific Instruments

Use `block_instruments` to disable specific instrumentations you don't want:

```python
from keywordsai_tracing import KeywordsAITelemetry, Instruments

telemetry = KeywordsAITelemetry(
    app_name="my-app",
    api_key="kwai-xxx",
    block_instruments={
        Instruments.REQUESTS,  # Don't trace HTTP requests
        Instruments.URLLIB3,   # Don't trace urllib3
        Instruments.REDIS,     # Don't trace Redis calls
    }
)
```

**Use case:** Reduce noise by blocking low-level HTTP instrumentations when you only care about high-level LLM calls.

#### Option 2: Enable Only Specific Instruments

Use `instruments` to enable only the instrumentations you want:

```python
from keywordsai_tracing import KeywordsAITelemetry, Instruments

telemetry = KeywordsAITelemetry(
    app_name="my-app",
    api_key="kwai-xxx",
    instruments={
        Instruments.OPENAI,      # Only trace OpenAI
        Instruments.ANTHROPIC,   # Only trace Anthropic
    }
)
```

**Use case:** Maximum performance and minimal noise - only instrument what you need.

#### Option 3: Disable All Instrumentation

Pass an empty set to disable all automatic instrumentation:

```python
from keywordsai_tracing import KeywordsAITelemetry

telemetry = KeywordsAITelemetry(
    app_name="my-app",
    api_key="kwai-xxx",
    instruments=set(),  # No auto-instrumentation
)
```

**Use case:** 
- Backend systems that only need `@workflow`/`@task` decorators
- Custom manual instrumentation only
- Minimal overhead

Even with `instruments=set()`, you can still:
- ✅ Use `@workflow` and `@task` decorators
- ✅ Create manual spans with `tracer.start_as_current_span()`
- ✅ Use `get_client()` to update spans
- ❌ Won't automatically trace OpenAI/Anthropic/etc calls

### Instrumentation Best Practices

#### 1. Install Only What You Need

```bash
# Bad: Installing all instrumentation packages (bloats dependencies)
pip install opentelemetry-instrumentation-openai \
            opentelemetry-instrumentation-anthropic \
            opentelemetry-instrumentation-langchain \
            # ... 30+ packages

# Good: Install only what you use
pip install opentelemetry-instrumentation-openai  # You use OpenAI
pip install opentelemetry-instrumentation-langchain  # You use LangChain
```

#### 2. Reduce Noise in Production

```python
# Development: Enable everything for visibility
dev_telemetry = KeywordsAITelemetry(
    app_name="my-app-dev"
)

# Production: Block low-level instrumentations to reduce noise
prod_telemetry = KeywordsAITelemetry(
    app_name="my-app-prod",
    block_instruments={
        Instruments.REQUESTS,
        Instruments.URLLIB3,
        Instruments.REDIS,
    }
)
```

#### 3. Backend Services: Minimal Instrumentation

```python
# Backend API: Disable auto-instrumentation, use decorators only
backend_telemetry = KeywordsAITelemetry(
    app_name="backend-api",
    instruments=set(),  # No auto-instrumentation
    is_batching_enabled=False,  # No background threads
)

# Manual instrumentation only
@workflow(name="api_endpoint")
def api_endpoint(data):
    # Your logic here
    pass
```

### Troubleshooting Instrumentation

#### Issue: "My OpenAI calls aren't being traced"

**Solution:** Install the instrumentation package:

```bash
pip install opentelemetry-instrumentation-openai
```

Verify it's working:

```python
from keywordsai_tracing import KeywordsAITelemetry

telemetry = KeywordsAITelemetry(log_level="DEBUG")
# Check logs for: "Initialized OpenAI instrumentation"
```

#### Issue: "Too many spans are being created (noise)"

**Solution:** Block unnecessary instrumentations:

```python
from keywordsai_tracing import Instruments

telemetry = KeywordsAITelemetry(
    block_instruments={
        Instruments.REQUESTS,  # Block HTTP client spans
        Instruments.URLLIB3,   # Block urllib3 spans
    }
)
```

#### Issue: "Performance overhead in my backend"

**Solution:** Disable auto-instrumentation entirely:

```python
telemetry = KeywordsAITelemetry(
    instruments=set(),  # No auto-instrumentation
    is_batching_enabled=False,  # No background threads
)
```

### Summary

| Configuration | Auto-Instrumentation | Use Case |
|--------------|---------------------|----------|
| Default | All available | Development, full visibility |
| `block_instruments={...}` | All except blocked | Production, reduce noise |
| `instruments={...}` | Only specified | Targeted tracing |
| `instruments=set()` | None | Backend, minimal overhead |

**Key Points:**
- ✅ Default: All instrumentations enabled (if packages installed)
- ✅ Install: `opentelemetry-instrumentation-<library>` for each library
- ✅ Control: Use `instruments` or `block_instruments` parameters
- ✅ Performance: Disable unused instrumentations to reduce overhead
- ✅ Flexibility: Can disable all auto-instrumentation and use decorators only

## Advanced Features

### Custom Exporters

If you need custom export logic (e.g., sending to an internal system instead of KeywordsAI API), you can provide your own `SpanExporter`:

```python
from keywordsai_tracing import KeywordsAITelemetry
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult

class CustomExporter(SpanExporter):
    """Custom exporter that sends spans to your internal system"""
    
    def export(self, spans):
        # Your custom export logic here
        for span in spans:
            # Send to your internal system
            my_internal_system.log(span)
        return SpanExportResult.SUCCESS
    
    def shutdown(self):
        pass
    
    def force_flush(self, timeout_millis=30000):
        return True

# Initialize with custom exporter
telemetry = KeywordsAITelemetry(
    app_name="my-app",
    custom_exporter=CustomExporter(),
)
```

When using a custom exporter, `api_key` and `base_url` parameters are not required since spans won't be sent to the KeywordsAI API.

**Use cases for custom exporters:**
- Internal integrations that need custom export logic
- Sending spans to custom backends or databases
- Writing spans to files for debugging
- Testing and development environments

#### Custom Exporter Initialization Pattern

When using custom exporters, **initialize once at application startup** and use `get_client()` for per-request operations:

```python
from keywordsai_tracing import KeywordsAITelemetry, get_client

# At app startup (e.g., settings.py, __init__.py)
exporter = MyCustomExporter()
telemetry = KeywordsAITelemetry(
    app_name="my-app",
    custom_exporter=exporter,
    is_batching_enabled=False,  # Optional: disable batching for immediate export
)

# Per-request: use get_client() to access SDK features
def handle_request():
    client = get_client()
    tracer = client.get_tracer()  # Get tracer for manual span creation
    
    with tracer.start_as_current_span("request_handler") as span:
        # Update span with request-specific attributes
        client.update_current_span(
            attributes={"request.id": "123"}
        )
        # Your request logic here
        pass
```

**Key Points:**
- ✅ Initialize telemetry **once** at startup with your custom exporter
- ✅ Use `get_client()` to access the SDK in your request handlers
- ✅ Use `client.get_tracer()` for manual span creation (public API)
- ✅ Use `client.update_current_span()` to add request-specific attributes

#### Custom Exporter with Per-Request Context

If your custom exporter needs per-request context (e.g., organization ID, user authentication, experiment ID), use Python's `contextvars` for thread-safe context storage:

```python
from contextvars import ContextVar
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult
from keywordsai_tracing import KeywordsAITelemetry, get_client

# Thread-safe context storage
_request_context: ContextVar[dict] = ContextVar('request_context', default={})

def set_request_context(**kwargs):
    """Set context for current request (thread-safe)."""
    _request_context.set(kwargs)

def get_request_context():
    """Get context for current request."""
    return _request_context.get()

def clear_request_context():
    """Clear context after request."""
    _request_context.set({})

class BackendExporter(SpanExporter):
    """Custom exporter that uses per-request context"""
    
    def export(self, spans):
        # Read per-request context (thread-safe)
        context = get_request_context()
        org_id = context.get('org_id')
        user_id = context.get('user_id')
        experiment_id = context.get('experiment_id')
        
        for span in spans:
            span_data = {
                'name': span.name,
                'attributes': dict(span.attributes),
                # Add context to each span
                'org_id': org_id,
                'user_id': user_id,
                'experiment_id': experiment_id,
            }
            # Send to your internal system
            self._send_to_backend(span_data)
        
        return SpanExportResult.SUCCESS
    
    def _send_to_backend(self, span_data):
        # Your backend logic (database, queue, API, etc.)
        pass
    
    def shutdown(self):
        pass
    
    def force_flush(self, timeout_millis=30000):
        return True

# At startup
exporter = BackendExporter()
telemetry = KeywordsAITelemetry(
    app_name="backend",
    custom_exporter=exporter,
    is_batching_enabled=False,
)

# Per-request usage
def handle_api_request(org_id, user_id, experiment_id):
    # Set context at the start of request
    set_request_context(
        org_id=org_id,
        user_id=user_id,
        experiment_id=experiment_id
    )
    
    try:
        # Use get_client() for span operations
        client = get_client()
        tracer = client.get_tracer()
        
        with tracer.start_as_current_span("api_request"):
            # Your request logic
            # Exporter will read context when exporting spans
            result = process_request()
            return result
    finally:
        # Clean up context after request
        clear_request_context()
```

**Why use `contextvars`?**
- ✅ **Thread-safe**: Each request/thread has isolated context
- ✅ **Async-safe**: Works with asyncio and concurrent execution
- ✅ **Automatic propagation**: Context flows through function calls
- ✅ **Clean separation**: Exporter initialization (startup) separate from request context

See [`examples/custom_exporter_example.py`](examples/custom_exporter_example.py) and [`examples/backend_trace_collection_example.py`](examples/backend_trace_collection_example.py) for complete working examples including:
- File exporter (writing spans to JSON lines)
- Console exporter (printing spans to terminal)
- Backend exporter with per-request context
- Direct logging exporter for immediate export

### Update Span Functionality

You can dynamically update spans while they're running using the `get_client()` API. This is useful for:
- Adding KeywordsAI-specific parameters (like `customer_identifier`, `trace_group_identifier`)
- Setting custom attributes during execution
- Adding events to track progress
- Recording exceptions and errors
- Changing span names based on runtime conditions

```python
from keywordsai_tracing import KeywordsAITelemetry, get_client, workflow
from openai import OpenAI

telemetry = KeywordsAITelemetry(
    app_name="my-app",
    api_key="kwai-xxx"
)

client = OpenAI()

@workflow(name="data_processing")
def process_data(user_id: str, data: dict):
    # Get the client to interact with the current span
    kwai_client = get_client()
    
    # Get current trace information
    trace_id = kwai_client.get_current_trace_id()
    span_id = kwai_client.get_current_span_id()
    print(f"Processing in trace: {trace_id}")
    
    # Update span with KeywordsAI-specific parameters
    kwai_client.update_current_span(
        keywordsai_params={
            "customer_identifier": user_id,
            "trace_group_identifier": "data-processing-pipeline",
            "metadata": {
                "data_size": len(str(data)),
                "processing_type": "batch"
            }
        }
    )
    
    # Add an event to track progress
    kwai_client.add_event("validation_started", {
        "record_count": len(data)
    })
    
    # Add custom attributes
    kwai_client.update_current_span(
        attributes={
            "custom.user_id": user_id,
            "custom.data_type": type(data).__name__
        }
    )
    
    try:
        # Call LLM
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": f"Process: {data}"}]
        )
        
        # Update span name based on result
        kwai_client.update_current_span(
            name="data_processing.success",
            attributes={"result_length": len(response.choices[0].message.content)}
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        # Record exception in the span
        kwai_client.record_exception(e)
        raise

# Use the workflow
result = process_data("user-123", {"key": "value"})
```

**Available Client Methods:**
- `get_current_trace_id()` - Get the current trace ID
- `get_current_span_id()` - Get the current span ID
- `get_tracer()` - Get the OpenTelemetry tracer for manual span creation
- `update_current_span()` - Update span with params, attributes, name, or status
- `add_event()` - Add an event to the current span
- `record_exception()` - Record an exception on the current span
- `is_recording()` - Check if the current span is recording
- `flush()` - Force flush all pending spans

See [`examples/simple_span_updating_example.py`](examples/simple_span_updating_example.py) for a complete example.

### Manual Span Creation

For fine-grained control, you can manually create custom spans using the tracer directly. This is useful when:
- You need spans that don't fit the `@workflow`/`@task` pattern
- You want to instrument specific code blocks
- You're integrating with existing tracing code
- You need to create spans conditionally

```python
from keywordsai_tracing import KeywordsAITelemetry, get_client

telemetry = KeywordsAITelemetry(
    app_name="my-app",
    api_key="keywordsai-xxx"
)

# Get the tracer instance using the public API
client = get_client()
tracer = client.get_tracer()

# Create a parent span manually
with tracer.start_as_current_span("database_operation") as parent_span:
    parent_span.set_attribute("db.system", "postgresql")
    parent_span.set_attribute("db.operation", "query")
    parent_span.add_event("Connection established")
    
    # Create nested child spans
    with tracer.start_as_current_span("execute_query") as query_span:
        query_span.set_attribute("db.statement", "SELECT * FROM users")
        query_span.set_attribute("db.rows_affected", 42)
        
        # You can still use get_client() within manual spans
        client = get_client()
        client.update_current_span(
            keywordsai_params={
                "customer_identifier": "admin-user"
            }
        )
        
        # Simulate query execution
        result = execute_database_query()
    
    with tracer.start_as_current_span("process_results") as process_span:
        process_span.set_attribute("result.count", len(result))
        processed = process_results(result)
    
    parent_span.add_event("Operation completed", {
        "total_time_ms": 150
    })
```

**Combining Manual Spans with Decorators:**

You can mix manual span creation with decorator-based spans:

```python
from keywordsai_tracing import workflow, task, get_client

@workflow(name="hybrid_workflow")
def hybrid_workflow(data):
    client = get_client()
    tracer = client.get_tracer()
    
    # Use decorator-based task
    validated_data = validate_data(data)
    
    # Create manual span for specific instrumentation
    with tracer.start_as_current_span("custom_processing") as span:
        span.set_attribute("processing.type", "custom")
        span.set_attribute("data.size", len(validated_data))
        
        # Custom processing logic
        for item in validated_data:
            with tracer.start_as_current_span(f"process_item_{item['id']}") as item_span:
                item_span.set_attribute("item.id", item['id'])
                process_single_item(item)
    
    # Use another decorator-based task
    return finalize_results(validated_data)

@task(name="validate_data")
def validate_data(data):
    # Decorator-based span
    return [item for item in data if item.get('valid')]

@task(name="finalize_results")
def finalize_results(data):
    # Decorator-based span
    return {"processed": len(data), "data": data}
```

**Thread-Safe Context Propagation:**

When working with threads, you can manually propagate context:

```python
from opentelemetry import context as otel_context
import threading

@workflow(name="threaded_workflow")
def threaded_workflow():
    client = get_client()
    tracer = client.get_tracer()
    
    # Capture the current context
    current_context = otel_context.get_current()
    
    def worker_function():
        # Attach the captured context in the worker thread
        token = otel_context.attach(current_context)
        
        try:
            # Create spans in the worker thread
            with tracer.start_as_current_span("worker_task") as span:
                span.set_attribute("thread.name", threading.current_thread().name)
                # Your work here
                pass
        finally:
            # Detach the context
            otel_context.detach(token)
    
    # Start worker thread
    thread = threading.Thread(target=worker_function)
    thread.start()
    thread.join()
```

**Key Points:**
- Use `tracer.start_as_current_span(name)` to create custom spans
- Spans automatically nest based on context
- You can mix manual spans with `@workflow` and `@task` decorators
- Use `get_client()` within manual spans to access client API
- Threading instrumentation is enabled by default for automatic context propagation across threads

See [`examples/custom_exporter_example.py`](examples/custom_exporter_example.py) for examples of manual span creation.

### Manual Span Buffering with SpanBuffer

For advanced use cases where you need to **manually control span buffering and export timing**, use the OpenTelemetry-compliant `SpanBuffer` context manager. Unlike the SDK's automatic background batch export, `SpanBuffer` gives you complete control over when spans are created and exported.

**Key Difference:**
- **Normal SDK behavior**: Spans are automatically exported in the background (via `BatchSpanProcessor`)
- **SpanBuffer**: Spans are buffered in a local queue and exported only when you explicitly call `export_spans()`

This is particularly useful for:

- **Asynchronous span creation**: Create spans after execution completes
- **Batch ingestion**: Collect multiple spans and export them with a single API call
- **Manual export control**: Decide when and whether to export collected spans
- **Trace-level batching**: Group all spans for a trace and export together

#### Basic Usage

```python
from keywordsai_tracing import KeywordsAITelemetry, get_client

telemetry = KeywordsAITelemetry(
    app_name="my-app",
    api_key="kwai-xxx"
)

client = get_client()

# Buffer spans in a local queue and export as batch
with client.get_span_buffer("trace-123") as buffer:
    # Create multiple spans - they go to local queue, not exported yet
    buffer.create_span("step1", {"status": "completed", "latency": 100})
    buffer.create_span("step2", {"status": "completed", "latency": 200})
    buffer.create_span("step3", {"status": "completed", "latency": 150})
    
    # Export all spans as a single batch
    buffer.export_spans()
```

#### Async Span Creation Pattern

Create spans after your workflow executes (useful for post-processing or logging):

```python
# Phase 1: Execute workflows (no tracing context)
results = []
for workflow in workflows:
    result = execute_workflow(workflow)  # No spans created during execution
    results.append(result)

# Phase 2: Create spans from completed results
with client.get_span_buffer("experiment-123") as buffer:
    for i, result in enumerate(results):
        buffer.create_span(
            f"workflow_{i}",
            attributes={
                "input": result["input"],
                "output": result["output"],
                "latency": result["latency"],
                "cost": result["cost"],
            }
        )
    
    # Single batch export for all spans
    buffer.export_spans()
```

#### Inspect Before Export

```python
with client.get_span_buffer("trace-123") as buffer:
    # Create spans
    buffer.create_span("task1", {"status": "completed", "score": 0.95})
    buffer.create_span("task2", {"status": "failed", "score": 0.45})
    buffer.create_span("task3", {"status": "completed", "score": 0.88})
    
    # Inspect spans before exporting
    print(f"Buffered {buffer.get_span_count()} spans")
    
    for span in buffer.get_all_spans():
        print(f"  - {span.name}: {dict(span.attributes)}")
    
    # Conditionally export based on inspection
    if buffer.get_span_count() > 0:
        buffer.export_spans()
```

#### SpanBuffer API

**Methods:**
- `create_span(name, attributes=None, kind=None)` - Create a span in the local queue
- `export_spans()` - Export all buffered spans as a batch (returns `True` on success)
- `get_all_spans()` - Get list of all buffered spans for inspection
- `get_span_count()` - Get the number of buffered spans
- `clear_spans()` - Discard all buffered spans without exporting

**Context Behavior:**
- Spans created with `buffer.create_span()` go to the buffer's local queue
- **ALL spans created within the buffer context** (including via tracer or decorators) are buffered
- Spans created outside the buffer context are exported normally
- Automatic cleanup when context exits

#### Important: Context Isolation

When you use `SpanBuffer`, **all spans created within that context** are buffered, including:
- Spans created via `buffer.create_span()`
- Spans created via `tracer.start_as_current_span()`
- Spans created by `@workflow` and `@task` decorators
- Auto-instrumented spans (OpenAI, Anthropic, etc.)

```python
client = get_client()
tracer = client.get_tracer()

# Normal span (exported immediately)
with tracer.start_as_current_span("before_buffer"):
    pass

# Buffer context - ALL spans buffered
with client.get_span_buffer("trace-123") as buffer:
    buffer.create_span("span1", {})  # Buffered
    
    with tracer.start_as_current_span("span2"):  # Also buffered!
        pass
    
    print(f"Total buffered: {buffer.get_span_count()}")  # Shows 2
    buffer.export_spans()  # Exports both spans

# Normal span (exported immediately)
with tracer.start_as_current_span("after_buffer"):
    pass
```

#### Use Cases

**Backend Workflow System:**
```python
# Workflow execution system that needs batch span creation
def ingest_workflow_output(workflow_result, trace_id, org_id, experiment_id):
    with client.get_span_collector(trace_id) as collector:
        # Create parent span
        collector.create_span(
            "workflow_execution",
            attributes={
                "input": workflow_result["input"],
                "output": workflow_result["output"],
                "experiment_id": experiment_id,
                "organization_id": org_id,
            }
        )
        
        # Create child spans for each step
        for step in workflow_result["steps"]:
            collector.create_span(
                f"step_{step['name']}",
                attributes={
                    "input": step["input"],
                    "output": step["output"],
                    "latency_ms": step["latency"],
                    "cost_usd": step["cost"],
                }
            )
        
        # Single batch export for entire trace
        success = collector.export_spans()
        return success
```

**Experiment Logging:**
```python
# Log multiple experiment runs as a single batch
experiment_results = run_experiments(configs)

with client.get_span_collector(f"experiment-{experiment_id}") as collector:
    for i, result in enumerate(experiment_results):
        collector.create_span(
            f"run_{i}",
            attributes={
                "config": result["config"],
                "metrics": result["metrics"],
                "success": result["success"],
            }
        )
    
    collector.export_spans()
```

**Benefits:**
- ✅ **Manual export timing**: Export only when you explicitly call `export_spans()` (vs automatic background export)
- ✅ **Conditional export**: Decide whether to export based on span inspection or business logic
- ✅ **Async span creation**: Create spans after execution completes (decouple execution from tracing)
- ✅ **Single API call per trace**: All spans in a trace exported together (vs individual span exports)
- ✅ **Inspection capability**: Review and modify spans before sending
- ✅ **Thread-safe isolation**: Uses context variables for proper isolation

See [`examples/span_collector_example.py`](examples/span_collector_example.py) for complete working examples.

# Keywords AI Instrumentation for Langfuse

Automatic instrumentation for Langfuse that sends all traces to Keywords AI.

## Installation

```bash
pip install keywordsai-instrumentation-langfuse
```

## Usage

### 1. Set Your API Key

```bash
export KEYWORDSAI_API_KEY="your-api-key"
```

### 2. Change Your Import

**Before:**
```python
from langfuse import Langfuse, observe
```

**After:**
```python
from keywordsai_instrumentation_langfuse import Langfuse, observe
```

That's it! All your Langfuse traces will now be sent to Keywords AI.

## Example

```python
import os
from keywordsai_instrumentation_langfuse import Langfuse, observe

langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
)

@observe(as_type="generation")
def chat_completion(user_message: str):
    return f"Response to: {user_message}"

@observe()
def my_workflow(query: str):
    result = chat_completion(query)
    return result

# Run your workflow
result = my_workflow("Hello!")

# Flush traces to Keywords AI
langfuse.flush()
```

## Custom Endpoint (Optional)

For self-hosted Keywords AI:

```python
from keywordsai_instrumentation_langfuse import patch_langfuse_exporter

patch_langfuse_exporter(
    api_key="your-api-key",
    endpoint="https://your-instance.com/api/v1/traces/ingest"
)

from langfuse import Langfuse, observe
```

## License

Apache 2.0

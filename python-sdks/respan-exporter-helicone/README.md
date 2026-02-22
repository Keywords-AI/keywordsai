# Respan Helicone Exporter

**[respan.ai](https://respan.ai)** | **[Documentation](https://docs.respan.ai)** | **[PyPI](https://pypi.org/project/respan-exporter-helicone/)**

Helicone integration for exporting manual logs to Respan.

## Installation

```bash
pip install respan-exporter-helicone
```

## Quick Start

```python
from respan_exporter_helicone import HeliconeInstrumentor
from helicone_helpers import HeliconeManualLogger
import time
import openai

# Setup instrumentation
instrumentor = HeliconeInstrumentor()
instrumentor.instrument(api_key="your-respan-api-key")

# Initialize Helicone logger
logger = HeliconeManualLogger(api_key="your-helicone-api-key")
client = openai.OpenAI(api_key="your-openai-api-key")

# Make LLM calls - traces are sent to both Helicone and Respan
request = {
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": "Hello!"}]
}

def chat_operation(result_recorder):
    response = client.chat.completions.create(**request)
    import json
    result_recorder.append_results(json.loads(response.to_json()))
    return response

logger.log_request(
    provider="openai",
    request=request,
    operation=chat_operation
)
```

## License

MIT

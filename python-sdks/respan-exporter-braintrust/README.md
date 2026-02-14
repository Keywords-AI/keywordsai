# Respan Braintrust Exporter

Send Braintrust logging data to Respan for tracing.

## Installation

```bash
pip install respan-exporter-braintrust
```

## Quick start

```python
import os
from braintrust import init_logger, wrap_openai
from openai import OpenAI
from respan_exporter_braintrust import RespanBraintrustExporter

os.environ["RESPAN_API_KEY"] = "your-respan-key"

with RespanBraintrustExporter() as exporter:
    logger = init_logger(project="Email Classifier")
    client = wrap_openai(OpenAI())

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Hello from Braintrust"}],
    )

    logger.log(
        input={"prompt": "Hello from Braintrust"},
        output=response.choices[0].message.content,
    )

    logger.flush()
```

## Configuration

Environment variables:

- `RESPAN_API_KEY` (required)
- `RESPAN_BASE_URL` (optional, default: `https://api.respan.ai/api`)

## Notes

- This exporter uses Braintrust log records and maps them to Respan trace fields.
- Root Braintrust spans become trace roots in Respan.

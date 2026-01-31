# KeywordsAI Braintrust Exporter

Send Braintrust logging data to Keywords AI for tracing.

## Installation

```bash
pip install keywordsai-exporter-braintrust
```

## Quick start

```python
import os
from braintrust import init_logger, wrap_openai
from openai import OpenAI
from keywordsai_exporter_braintrust import KeywordsAIExporter

os.environ["KEYWORDSAI_API_KEY"] = "your-keywordsai-key"

with KeywordsAIExporter() as exporter:
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

- `KEYWORDSAI_API_KEY` (required)
- `KEYWORDSAI_BASE_URL` (optional, default: `https://api.keywordsai.co/api`)

## Notes

- This exporter uses Braintrust log records and maps them to Keywords AI trace fields.
- Root Braintrust spans become trace roots in Keywords AI.

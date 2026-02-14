# Respan Exporter for Superagent

Exports `safety-agent` (Superagent) calls to Respan traces ingestion.

## Installation

```bash
pip install respan-exporter-superagent
```

## Usage

```python
import os
from respan_exporter_superagent import create_client

client = create_client(
    api_key=os.getenv("RESPAN_API_KEY"),
    endpoint=os.getenv("RESPAN_ENDPOINT"),  # optional
)

result = await client.guard(
    input="hello",
    keywordsai_params={
        "workflow_name": "wf",
        "span_name": "sp",
        "customer_identifier": "user-123",
    },
)
print(result)
```

## Environment variables

- `RESPAN_API_KEY`: API key used for ingest authorization.
- `RESPAN_ENDPOINT`: optional override for ingest endpoint.

Backwards-compatible aliases (if you already use KeywordsAI env vars):

- `KEYWORDSAI_API_KEY`
- `KEYWORDSAI_ENDPOINT`


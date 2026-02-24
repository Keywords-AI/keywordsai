# respan-exporter-dify

Respan exporter for Dify AI Python SDK (`dify-client-python`).

## Installation

```bash
pip install respan-exporter-dify
```

## Usage

```python
from dify_client import Client
from respan_exporter_dify.exporter import create_client

dify_client = Client(api_key="your-dify-api-key")

# Wrap the client
respan_client = create_client(
    client=dify_client,
    api_key="your-respan-api-key"
)

# Use it as a normal Dify Client
# The requests are automatically logged to Respan!
```

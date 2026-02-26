# Respan Exporter for Agno

**[respan.ai](https://respan.ai)** | **[Documentation](https://docs.respan.ai)** | **[PyPI](https://pypi.org/project/respan-exporter-agno/)**

Respan exporter for Agno traces.

## Installation

```bash
pip install respan-exporter-agno
```

## Usage

```python
import os
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from respan_exporter_agno import RespanAgnoInstrumentor

RespanAgnoInstrumentor().instrument(api_key="your-respan-api-key")

agent = Agent(
    name="Example Agent",
    model=OpenAIChat(id="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY")),
)
agent.run("hello from agno")
```

## Gateway Calls (optional)

```python
import os
from agno.agent import Agent
from agno.models.openai import OpenAIChat

gateway_base_url = os.getenv(
    "RESPAN_GATEWAY_BASE_URL",
    "https://api.respan.ai/api",
)
agent = Agent(
    name="Gateway Agent",
    model=OpenAIChat(
        id="gpt-4o-mini",
        api_key=os.getenv("RESPAN_API_KEY"),
        base_url=gateway_base_url,
    ),
)
agent.run("hello from Respan gateway")
```

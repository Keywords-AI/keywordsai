# Keywords AI Exporter for Agno

## Installation

```bash
pip install keywordsai-exporter-agno
```

## Usage

```python
import os
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from keywordsai_exporter_agno import KeywordsAIAgnoInstrumentor

KeywordsAIAgnoInstrumentor().instrument(api_key="your-keywordsai-api-key")

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
    "KEYWORDSAI_GATEWAY_BASE_URL",
    "https://api.keywordsai.co/api",
)
agent = Agent(
    name="Gateway Agent",
    model=OpenAIChat(
        id="gpt-4o-mini",
        api_key=os.getenv("KEYWORDSAI_API_KEY"),
        base_url=gateway_base_url,
    ),
)
agent.run("hello from KeywordsAI gateway")
```

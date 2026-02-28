# Respan Exporter for CrewAI

**[respan.ai](https://respan.ai)** | **[Documentation](https://docs.respan.ai)** | **[PyPI](https://pypi.org/project/respan-exporter-crewai/)**

Respan exporter for CrewAI traces.

## Installation

```bash
pip install respan-exporter-crewai
```

## Usage

```python
import os
from crewai import Agent, Task, Crew
from respan_exporter_crewai import RespanCrewAIInstrumentor

RespanCrewAIInstrumentor().instrument(api_key="your-respan-api-key")

agent = Agent(
    role='Example Agent',
    goal='Provide a friendly greeting',
    backstory='You are a helpful assistant',
)

task = Task(
    description='Say hello to the user',
    expected_output='A greeting message',
    agent=agent
)

crew = Crew(
    agents=[agent],
    tasks=[task],
)

crew.kickoff()
```

## Gateway Calls (optional)

```python
import os
from crewai import Agent, Task, Crew

os.environ["OPENAI_BASE_URL"] = os.getenv(
    "RESPAN_GATEWAY_BASE_URL",
    "https://api.respan.ai/api",
)
os.environ["OPENAI_API_KEY"] = os.getenv("RESPAN_API_KEY", "your-respan-api-key")

agent = Agent(
    role='Gateway Agent',
    goal='Provide a gateway response',
    backstory='You are a helpful gateway router',
)

task = Task(
    description='Say hello from Respan gateway',
    expected_output='A greeting message',
    agent=agent
)

crew = Crew(agents=[agent], tasks=[task])
crew.kickoff()
```

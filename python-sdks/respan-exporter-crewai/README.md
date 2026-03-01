# Respan Exporter for CrewAI

**[respan.ai](https://respan.ai)** | **[Documentation](https://docs.respan.ai)** | **[PyPI](https://pypi.org/project/respan-exporter-crewai/)**

Respan exporter for CrewAI traces. Sends CrewAI workflow, agent, task, and tool spans to Respan for tracing and observability.

## Installation

```bash
pip install respan-exporter-crewai
```

This installs `openinference-instrumentation-crewai` as a runtime dependency so the instrumentor can intercept OpenTelemetry spans from CrewAI.

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

## What gets captured

- **Trace hierarchy** — workflow → agents → tasks → tools in one trace
- **Agent / task / tool spans** — names, inputs, outputs, and span kinds
- **Token usage** — prompt and completion tokens when available
- **Latency** — start/end times and duration per span

## Configuration

| Env Var | Required | Default |
|---------|----------|---------|
| `RESPAN_API_KEY` | Yes (or pass `api_key=` to `instrument()`) | — |
| `RESPAN_BASE_URL` | No | `https://api.respan.ai/api` |
| `RESPAN_ENDPOINT` | No | `{base_url}/v1/traces/ingest` |

## Gateway Calls (optional)

Route all LLM calls through Respan's gateway for automatic logging, cost tracking, and fallbacks — no extra instrumentor needed.

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

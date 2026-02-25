# Respan Exporter for Anthropic Agent SDK

**[respan.ai](https://respan.ai)** | **[Documentation](https://respan.ai/docs)**

Exporter for Anthropic Agent SDK telemetry to Respan.

## Quickstart

```python
import asyncio
from claude_agent_sdk import ClaudeAgentOptions
from respan_exporter_anthropic_agents.respan_anthropic_agents_exporter import (
    RespanAnthropicAgentsExporter,
)

exporter = RespanAnthropicAgentsExporter()

async def main() -> None:
    options = exporter.with_options(
        options=ClaudeAgentOptions(
            allowed_tools=["Read", "Glob", "Grep"],
            permission_mode="acceptEdits",
        )
    )

    async for message in exporter.query(
        prompt="Analyze this repository and summarize architecture.",
        options=options,
    ):
        print(message)

asyncio.run(main())
```

## Real Gateway Integration Test

Run the live integration test to verify:
- Claude Agent SDK traffic goes through Respan gateway (no direct Anthropic key required).
- Exporter uploads tracing payloads to real Respan ingest endpoint.

Required environment variables:

```bash
export RUN_REAL_GATEWAY_TEST=1
export RESPAN_API_KEY="your_respan_key"
```

Optional environment variables:

```bash
# Defaults to RESPAN_BASE_URL, KEYWORDSAI_BASE_URL, then https://api.respan.ai
export RESPAN_GATEWAY_BASE_URL="https://api.respan.ai"

# Optional Anthropic-compatible gateway base URL override
export RESPAN_ANTHROPIC_BASE_URL="https://api.respan.ai"

# Optional model override
export RESPAN_GATEWAY_MODEL="claude-sonnet-4-5"
```

Run test:

```bash
python -m unittest tests.test_real_gateway_integration -v
```


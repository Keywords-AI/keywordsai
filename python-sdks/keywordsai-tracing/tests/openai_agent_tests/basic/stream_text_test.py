from dotenv import load_dotenv

load_dotenv("./tests/.env", override=True)

endpoint = "http://localhost:8000/api/openai/v1/traces/ingest"
import pytest
import time
import os
import asyncio


from openai.types.responses import ResponseTextDeltaEvent

from agents import Agent, Runner

from keywordsai_tracing.integrations.openai_agents_integration import (
    KeywordsAITraceProcessor,
)
from agents.tracing import set_trace_processors, trace

set_trace_processors(
    [
        KeywordsAITraceProcessor(os.getenv("KEYWORDSAI_API_KEY"), endpoint=os.getenv("KEYWORDSAI_OAIA_TRACING_ENDPOINT")),
    ]
)


@pytest.mark.asyncio
async def test_main():
    agent = Agent(
        name="Joker",
        instructions="You are a helpful assistant.",
    )

    with trace("Stream jokes test"):
        result = Runner.run_streamed(agent, input="Please tell me 5 jokes.")
        async for event in result.stream_events():
            if event.type == "raw_response_event" and isinstance(
                event.data, ResponseTextDeltaEvent
            ):
                print(event.data.delta, end="", flush=True)


if __name__ == "__main__":
    asyncio.run(test_main())
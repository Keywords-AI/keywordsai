from dotenv import load_dotenv

load_dotenv("./tests/.env", override=True)

endpoint = "http://localhost:8000/api/openai/v1/traces/ingest"
import time
import os
import asyncio


from openai.types.responses import ResponseTextDeltaEvent

from agents import Agent, Runner

from keywordsai_tracing.integrations.openai_agents_integration import (
    KeywordsAITraceProcessor,
)
from agents.tracing import set_trace_processors

set_trace_processors(
    [
        KeywordsAITraceProcessor(os.getenv("KEYWORDSAI_API_KEY"), endpoint=endpoint),
    ]
)


async def main():
    agent = Agent(
        name="Joker",
        instructions="You are a helpful assistant.",
    )

    result = Runner.run_streamed(agent, input="Please tell me 5 jokes.")
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(
            event.data, ResponseTextDeltaEvent
        ):
            print(event.data.delta, end="", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
    time.sleep(1000)

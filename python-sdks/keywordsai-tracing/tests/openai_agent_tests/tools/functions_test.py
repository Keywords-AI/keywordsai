from dotenv import load_dotenv

load_dotenv("./tests/.env", override=True)
import pytest
# ==========copy the below==========
import asyncio
from agents import Agent, Runner, function_tool
from keywordsai_tracing.integrations.openai_agents_integration import (
    KeywordsAITraceProcessor,
)
from agents.tracing import set_trace_processors
import os

set_trace_processors(
    [
        KeywordsAITraceProcessor(
            os.getenv("KEYWORDSAI_API_KEY"),
            endpoint="http://localhost:8000/api/openai/v1/traces/ingest",
        ),
    ]
)


@function_tool
def get_weather(city: str) -> str:
    return f"The weather in {city} is sunny."


agent = Agent(
    name="Hello world",
    instructions="You are a helpful agent.",
    tools=[get_weather],
)


@pytest.mark.asyncio
async def test_main():
    result = await Runner.run(agent, input="What's the weather in Tokyo?")
    print(result.final_output)
    # The weather in Tokyo is sunny.

if __name__ == "__main__":
    asyncio.run(test_main())

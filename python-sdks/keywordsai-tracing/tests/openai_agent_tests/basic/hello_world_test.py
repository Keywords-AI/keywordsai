from dotenv import load_dotenv

load_dotenv("./tests/.env", override=True)
import pytest
# ==========copy paste below==========
import asyncio
import os
from agents import Agent, Runner
from agents.tracing import set_trace_processors, trace
from keywordsai_tracing.integrations.openai_agents_integration import KeywordsAITraceProcessor

set_trace_processors(
    [
        KeywordsAITraceProcessor(
            api_key=os.getenv("KEYWORDSAI_API_KEY"),
            endpoint=os.getenv("KEYWORDSAI_OAIA_TRACING_ENDPOINT"),
        ),
    ]
)


@pytest.mark.asyncio
async def test_main():
    agent = Agent(
        name="Assistant",
        instructions="You only respond in haikus.",
    )

    with trace("Hello world test"):
        result = await Runner.run(agent, "Tell me about recursion in programming.")
        print(result.final_output)
    # Function calls itself,
    # Looping in smaller pieces,
    # Endless by design.


if __name__ == "__main__":
    asyncio.run(test_main())

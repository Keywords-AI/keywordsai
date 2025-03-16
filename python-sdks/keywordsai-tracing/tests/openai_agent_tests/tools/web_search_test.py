from dotenv import load_dotenv

load_dotenv("./tests/.env", override=True)

import os
import asyncio
import pytest

from agents import Agent, Runner, WebSearchTool, trace
from agents.tracing import set_trace_processors
from keywordsai_tracing.integrations.openai_agents_integration import (
    KeywordsAITraceProcessor,
)

set_trace_processors(
    [KeywordsAITraceProcessor(os.getenv("KEYWORDSAI_API_KEY"), endpoint=os.getenv("KEYWORDSAI_OAIA_TRACING_ENDPOINT"))]
)


@pytest.mark.asyncio
async def test_main():
    agent = Agent(
        name="Web searcher",
        instructions="You are a helpful agent.",
        tools=[WebSearchTool(user_location={"type": "approximate", "city": "New York"})],
    )

    with trace("Web search example"):
        result = await Runner.run(
            agent,
            "search the web for 'local sports news' and give me 1 interesting update in a sentence.",
        )
        print(result.final_output)
        # The New York Giants are reportedly pursuing quarterback Aaron Rodgers after his ...

if __name__ == "__main__":
    asyncio.run(test_main())

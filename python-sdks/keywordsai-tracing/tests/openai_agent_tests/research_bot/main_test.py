from dotenv import load_dotenv

loaded = load_dotenv("./tests/.env", override=True)
import pytest
import os
import asyncio


from .manager import ResearchManager
from agents import set_trace_processors, trace
from keywordsai_tracing.integrations.openai_agents_integration import (
    KeywordsAITraceProcessor,
)

set_trace_processors(
    [KeywordsAITraceProcessor(os.getenv("KEYWORDSAI_API_KEY"), endpoint=os.getenv("KEYWORDSAI_OAIA_TRACING_ENDPOINT"))]
)


@pytest.mark.asyncio
async def test_main() -> None:
    query = "What is the capital of France?"
    await ResearchManager().run(query)


if __name__ == "__main__":
    asyncio.run(test_main())

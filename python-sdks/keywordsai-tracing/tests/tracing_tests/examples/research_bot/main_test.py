from dotenv import load_dotenv

loaded = load_dotenv("./tests/.env", override=True)
endpoint = "http://localhost:8000/api/openai/v1/traces/ingest"
import os
import asyncio


from .manager import ResearchManager
from agents import set_trace_processors
from keywordsai_tracing.integrations.openai_agents_integration import (
    KeywordsAITraceProcessor,
)

set_trace_processors(
    [KeywordsAITraceProcessor(os.getenv("KEYWORDSAI_API_KEY"), endpoint=endpoint)]
)


async def main() -> None:
    query = input("What would you like to research? ")
    await ResearchManager().run(query)


if __name__ == "__main__":
    asyncio.run(main())

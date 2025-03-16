from dotenv import load_dotenv

load_dotenv("./tests/.env", override=True)
import pytest
import os
import asyncio

from agents import Agent, FileSearchTool, Runner, trace
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
        name="File searcher",
        instructions="You are a helpful agent.",
        tools=[
            FileSearchTool(
                max_num_results=3,
                vector_store_ids=["vs_67d3bdd0c8888191adfa890a9e829480"],
                include_search_results=True,
            )
        ],
    )

    with trace("File search example"):
        result = await Runner.run(
            agent, "Be concise, and tell me 1 sentence about the gist of Landing Lease."
        )
        print(result.final_output)
        """
        Arrakis, the desert planet in Frank Herbert's "Dune," was inspired by the scarcity of water
        as a metaphor for oil and other finite resources.
        """

        print("\n".join([str(out) for out in result.new_items]))
        """
        {"id":"...", "queries":["Arrakis"], "results":[...]}
        """

if __name__ == "__main__":
    asyncio.run(test_main())

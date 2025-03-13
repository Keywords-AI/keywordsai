from dotenv import load_dotenv

load_dotenv("./tests/.env", override=True)

# ==========copy paste below==========
import asyncio
import os
from agents import Agent, Runner
from agents.tracing import set_trace_processors
from keywordsai_tracing.integrations.openai_agents_integration import KeywordsAITraceProcessor

set_trace_processors(
    [
        KeywordsAITraceProcessor(
            api_key=os.getenv("KEYWORDSAI_API_KEY"),
            endpoint="http://localhost:8000/api/openai/v1/traces/ingest",
        ),
    ]
)


async def main():
    agent = Agent(
        name="Assistant",
        instructions="You only respond in haikus.",
    )

    result = await Runner.run(agent, "Tell me about recursion in programming.")
    print(result.final_output)
    # Function calls itself,
    # Looping in smaller pieces,
    # Endless by design.


if __name__ == "__main__":
    asyncio.run(main())

from dotenv import load_dotenv

load_dotenv("./tests/.env", override=True)

# ==========copy the below==========
from agents import Agent, Runner
import asyncio
from keywordsai_tracing.integrations.openai_agents_integration import KeywordsAITraceProcessor
from agents.tracing import set_trace_processors
import os
set_trace_processors(
    [
        KeywordsAITraceProcessor(
            api_key=os.getenv("KEYWORDSAI_API_KEY"),
            endpoint="http://localhost:8000/api/openai/v1/traces/ingest",
        ),
    ]
)

spanish_agent = Agent(
    name="Spanish agent",
    instructions="You only speak Spanish.",
)

english_agent = Agent(
    name="English agent",
    instructions="You only speak English",
)

triage_agent = Agent(
    name="Triage agent",
    instructions="Handoff to the appropriate agent based on the language of the request.",
    handoffs=[spanish_agent, english_agent],
)


async def main():
    result = await Runner.run(triage_agent, input="Hola, ¿cómo estás?")
    print(result.final_output)
    # ¡Hola! Estoy bien, gracias por preguntar. ¿Y tú, cómo estás?

import time
if __name__ == "__main__":
    asyncio.run(main())
    time.sleep(100)
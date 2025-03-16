import asyncio
from dotenv import load_dotenv

load_dotenv("./tests/.env", override=True)
import pytest
from agents import Agent, ItemHelpers, Runner, trace
from keywordsai_tracing.integrations.openai_agents_integration import (
    KeywordsAITraceProcessor,
)
from agents.tracing import set_trace_processors
import os

set_trace_processors(
    [
        KeywordsAITraceProcessor(
            os.getenv("KEYWORDSAI_API_KEY"),
            endpoint=os.getenv("KEYWORDSAI_OAIA_TRACING_ENDPOINT"),
        ),
    ]
)
"""
This example shows the parallelization pattern. We run the agent three times in parallel, and pick
the best result.
"""
spanish_agent = Agent(
    name="spanish_agent",
    instructions="You translate the user's message to Spanish",
)

translation_picker = Agent(
    name="translation_picker",
    instructions="You pick the best Spanish translation from the given options.",
)


@pytest.mark.asyncio
async def test_main():
    msg = "Good morning, Agent!"

    # Ensure the entire workflow is a single trace
    with trace("Parallel translation"):
        res_1, res_2, res_3 = await asyncio.gather(
            Runner.run(
                spanish_agent,
                msg,
            ),
            Runner.run(
                spanish_agent,
                msg,
            ),
            Runner.run(
                spanish_agent,
                msg,
            ),
        )

        outputs = [
            ItemHelpers.text_message_outputs(res_1.new_items),
            ItemHelpers.text_message_outputs(res_2.new_items),
            ItemHelpers.text_message_outputs(res_3.new_items),
        ]

        translations = "\n\n".join(outputs)
        print(f"\n\nTranslations:\n\n{translations}")

        best_translation = await Runner.run(
            translation_picker,
            f"Input: {msg}\n\nTranslations:\n{translations}",
        )

    print("\n\n-----")

    print(f"Best translation: {best_translation.final_output}")


if __name__ == "__main__":
    asyncio.run(test_main())

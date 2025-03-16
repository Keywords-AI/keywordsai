from dotenv import load_dotenv

load_dotenv("./tests/.env", override=True)
import pytest
import asyncio
import uuid

from openai.types.responses import ResponseContentPartDoneEvent, ResponseTextDeltaEvent

from agents import Agent, RawResponsesStreamEvent, Runner, TResponseInputItem, trace
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
This example shows the handoffs/routing pattern. The triage agent receives the first message, and
then hands off to the appropriate agent based on the language of the request. Responses are
streamed to the user.
"""
french_agent = Agent(
    name="french_agent",
    instructions="You only speak French",
)

spanish_agent = Agent(
    name="spanish_agent",
    instructions="You only speak Spanish",
)

english_agent = Agent(
    name="english_agent",
    instructions="You only speak English",
)

triage_agent = Agent(
    name="triage_agent",
    instructions="Handoff to the appropriate agent based on the language of the request.",
    handoffs=[french_agent, spanish_agent, english_agent],
)


@pytest.mark.asyncio
async def test_main():
    # We'll create an ID for this conversation, so we can link each trace
    conversation_id = str(uuid.uuid4().hex[:16])

    agent = triage_agent
    inputs: list[TResponseInputItem] = [{"content": "Can you help me with my math homework?", "role": "user"}]
    questions = ["Can you help me with my math homework?", "Yeah, how to solve for x: 2x + 5 = 11?", "What's the capital of France?", ""]

    with trace("Routing example", group_id=conversation_id):
        for question in questions:
            # Each conversation turn is a single trace. Normally, each input from the user would be an
            # API request to your app, and you can wrap the request in a trace()

            result = Runner.run_streamed(
                agent,
                input=inputs,
            )
            async for event in result.stream_events():
                if not isinstance(event, RawResponsesStreamEvent):
                    continue
                data = event.data
                if isinstance(data, ResponseTextDeltaEvent):
                    print(data.delta, end="", flush=True)
                elif isinstance(data, ResponseContentPartDoneEvent):
                    print("\n")

            inputs = result.to_input_list()
            print("\n")
            if question == "":
                break
            inputs.append({"content": question, "role": "user"})
            agent = result.current_agent

if __name__ == "__main__":
    asyncio.run(test_main())

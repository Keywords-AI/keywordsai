from __future__ import annotations
from dotenv import load_dotenv

load_dotenv("./tests/.env", override=True)

import asyncio
import os
from typing import Literal, Union
import pytest
from pydantic import BaseModel

from agents import Agent, ItemHelpers, Runner, TResponseInputItem, trace
from keywordsai_tracing.integrations.openai_agents_integration import KeywordsAITraceProcessor
from agents.tracing import set_trace_processors


set_trace_processors(
    [
        KeywordsAITraceProcessor(
            os.getenv("KEYWORDSAI_API_KEY"),
            endpoint=os.getenv("KEYWORDSAI_OAIA_TRACING_ENDPOINT"),
        ),
    ]
)
"""
This example shows the LLM as a judge pattern. The first agent generates an outline for a story.
The second agent judges the outline and provides feedback. We loop until the judge is satisfied
with the outline.
"""

story_outline_generator = Agent(
    name="story_outline_generator",
    instructions=(
        "You generate a very short story outline based on the user's input."
        "If there is any feedback provided, use it to improve the outline."
    ),
)


class EvaluationFeedback(BaseModel):
    score: Literal["pass", "needs_improvement", "fail"]
    feedback: str


class StoryEvaluationResult(BaseModel):
    final_outline: str
    iterations: int
    final_score: str


evaluator = Agent[None](
    name="evaluator",
    instructions=(
        "You evaluate a story outline and decide if it's good enough."
        "If it's not good enough, you provide feedback on what needs to be improved."
        "Never give it a pass on the first try."
    ),
    output_type=EvaluationFeedback,
)


@pytest.mark.asyncio
async def test_main() -> StoryEvaluationResult:
    msg = "Sci fi"
    input_items: list[TResponseInputItem] = [{"content": msg, "role": "user"}]

    latest_outline: Union[str, None] = None
    iterations = 0
    max_iterations = 2
    final_score = ""
    
    # We'll run the entire workflow in a single trace
    with trace("LLM as a judge"):
        while True:
            iterations += 1
            if iterations > max_iterations:
                break

            story_outline_result = await Runner.run(
                story_outline_generator,
                input_items,
            )

            input_items = story_outline_result.to_input_list()
            latest_outline = ItemHelpers.text_message_outputs(story_outline_result.new_items)

            evaluator_result = await Runner.run(evaluator, input_items)
            result: EvaluationFeedback = evaluator_result.final_output
            final_score = result.score

            if result.score == "pass":
                break

            input_items.append({"content": f"Feedback: {result.feedback}", "role": "user"})

    return StoryEvaluationResult(
        final_outline=latest_outline or "",
        iterations=iterations,
        final_score=final_score
    )

if __name__ == "__main__":
    result = asyncio.run(test_main())
    print(f"Final story outline after {result.iterations} iterations (score: {result.final_score}):")
    print(result.final_outline)

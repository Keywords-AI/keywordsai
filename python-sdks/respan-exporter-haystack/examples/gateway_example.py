"""Simple gateway example for Keywords AI Haystack integration."""

import os
from haystack import Pipeline
from haystack.components.builders import PromptBuilder
from respan_exporter_haystack.gateway import RespanGenerator

# Create pipeline
pipeline = Pipeline()
pipeline.add_component(
    name="prompt",
    instance=PromptBuilder(template="Tell me about {{topic}}."),
)
pipeline.add_component(
    name="llm",
    instance=RespanGenerator(
    model="gpt-4o-mini",
    api_key=os.getenv("RESPAN_API_KEY") or os.getenv("KEYWORDSAI_API_KEY")
),
)
pipeline.connect(sender="prompt", receiver="llm")

# Run
result = pipeline.run({"prompt": {"topic": "machine learning"}})
print(result["llm"]["replies"][0])

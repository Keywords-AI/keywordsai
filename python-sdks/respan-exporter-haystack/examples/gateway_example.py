"""Simple gateway example for Respan Haystack integration."""

import os
from haystack import Pipeline
from haystack.components.builders import PromptBuilder
from respan_exporter_haystack import RespanGenerator

# Create pipeline
pipeline = Pipeline()
pipeline.add_component("prompt", PromptBuilder(template="Tell me about {{topic}}."))
pipeline.add_component("llm", RespanGenerator(
    model="gpt-4o-mini",
    api_key=os.getenv("RESPAN_API_KEY")
))
pipeline.connect("prompt", "llm")

# Run
result = pipeline.run({"prompt": {"topic": "machine learning"}})
print(result["llm"]["replies"][0])

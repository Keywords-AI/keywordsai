"""Simple gateway example for Keywords AI Haystack integration."""

import os
from haystack import Pipeline
from haystack.components.builders import PromptBuilder
from keywordsai_exporter_haystack import KeywordsAIGenerator

# Create pipeline
pipeline = Pipeline()
pipeline.add_component("prompt", PromptBuilder(template="Tell me about {{topic}}."))
pipeline.add_component("llm", KeywordsAIGenerator(
    model="gpt-4o-mini",
    api_key=os.getenv("KEYWORDSAI_API_KEY")
))
pipeline.connect("prompt", "llm")

# Run
result = pipeline.run({"prompt": {"topic": "machine learning"}})
print(result["llm"]["replies"][0])

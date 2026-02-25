"""Simple tracing example for Respan Haystack integration."""

import os
from haystack import Pipeline
from haystack.components.builders import PromptBuilder
from haystack.components.generators import OpenAIGenerator
from respan_exporter_haystack import RespanConnector

os.environ["HAYSTACK_CONTENT_TRACING_ENABLED"] = "true"

# Create pipeline with tracing
pipeline = Pipeline()
pipeline.add_component("tracer", RespanConnector("My Workflow"))
pipeline.add_component("prompt", PromptBuilder(template="Tell me about {{topic}}."))
pipeline.add_component("llm", OpenAIGenerator(model="gpt-4o-mini"))
pipeline.connect("prompt", "llm")

# Run
result = pipeline.run({"prompt": {"topic": "artificial intelligence"}})
print(result["llm"]["replies"][0])
print(f"\nTrace URL: {result['tracer']['trace_url']}")

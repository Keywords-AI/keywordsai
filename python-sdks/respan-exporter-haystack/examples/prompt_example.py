"""Simple prompt management example for Keywords AI Haystack integration."""

import os
from haystack import Pipeline
from keywordsai_exporter_haystack import KeywordsAIGenerator

# Create pipeline with platform prompt
pipeline = Pipeline()
pipeline.add_component("llm", KeywordsAIGenerator(
    prompt_id="1210b368ce2f4e5599d307bc591d9b7a",
    api_key=os.getenv("KEYWORDSAI_API_KEY")
))

# Run with prompt variables
result = pipeline.run({
    "llm": {
        "prompt_variables": {
            "user_input": "The cat sat on the mat"
        }
    }
})

print("Response received successfully!")
print(f"Model: {result['llm']['meta'][0]['model']}")
print(f"Tokens: {result['llm']['meta'][0]['usage']['total_tokens']}")

"""
Example: Tracing LLM generations with @observe(as_type="generation")
"""
import os
from keywordsai_instrumentation_langfuse import LangfuseInstrumentor

os.environ["KEYWORDSAI_API_KEY"] = "your-api-key"

# Instrument first
instrumentor = LangfuseInstrumentor()
instrumentor.instrument(api_key=os.environ["KEYWORDSAI_API_KEY"])

from langfuse import Langfuse, observe

langfuse = Langfuse(
    public_key="pk-lf-...",
    secret_key="sk-lf-..."
)

@observe(as_type="generation")
def generate_response(prompt: str):
    """Marked as a generation for better tracking."""
    return f"Generated: {prompt}"

result = generate_response("Write a poem")
print(result)

langfuse.flush()

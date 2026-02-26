"""
Basic example: Using @observe decorator with Langfuse
Data is automatically sent to Respan
"""
import dotenv
dotenv.load_dotenv(".env", override=True)

import os
from respan_instrumentation_langfuse import LangfuseInstrumentor

# Instrument BEFORE importing Langfuse
instrumentor = LangfuseInstrumentor()
instrumentor.instrument(api_key=os.environ["RESPAN_API_KEY"], endpoint=os.environ["RESPAN_BASE_URL"] + "/v1/traces/ingest")

# Now import and use Langfuse normally
from langfuse import Langfuse, observe

# Initialize Langfuse
langfuse = Langfuse(
    public_key="pk-lf-...",
    secret_key="sk-lf-...",
    host="https://cloud.langfuse.com"
)

@observe()
def process_query(query: str):
    """Simple function with tracing."""
    return f"Response to: {query}"

# Use the function
result = process_query("Hello World")
print(result)

# Flush to send data
langfuse.flush()

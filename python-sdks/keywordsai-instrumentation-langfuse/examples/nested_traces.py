"""
Example: Nested traces with parent-child relationships
"""
import os
from keywordsai_instrumentation_langfuse import LangfuseInstrumentor

os.environ["KEYWORDSAI_API_KEY"] = "your-api-key"

instrumentor = LangfuseInstrumentor()
instrumentor.instrument(api_key=os.environ["KEYWORDSAI_API_KEY"])

from langfuse import Langfuse, observe

langfuse = Langfuse(
    public_key="pk-lf-...",
    secret_key="sk-lf-..."
)

@observe()
def subtask(name: str):
    return f"Completed: {name}"

@observe()
def main_workflow(task: str):
    """Parent trace that calls child traces."""
    result1 = subtask("step 1")
    result2 = subtask("step 2")
    return f"Workflow done: {task}"

result = main_workflow("Process request")
print(result)

langfuse.flush()

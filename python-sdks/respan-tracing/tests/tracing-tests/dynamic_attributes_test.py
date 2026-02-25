from dotenv import load_dotenv
load_dotenv(override=True)

from respan_tracing.contexts.span import respan_span_attributes
from openai import OpenAI
from respan_tracing import RespanTelemetry
from respan_tracing.decorators import workflow, task
import os

k_tl = RespanTelemetry()
client = OpenAI()

os.environ["RESPAN_API_KEY"] = "test"
os.environ["RESPAN_BASE_URL"] = "https://api.respan.ai/api"
os.environ["RESPAN_API_KEY"] = os.getenv("RESPAN_API_KEY")

@workflow(name="test_dynamic_attributes")
def test_dynamic_attributes():
    with respan_span_attributes(
        respan_params={
            "trace_group_identifier": "test_dynamic_attributes",
        }
    ):
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Hello, world!"}],
        )
    return response

if __name__ == "__main__":
    test_dynamic_attributes()

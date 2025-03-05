from dotenv import load_dotenv
load_dotenv(override=True)

from keywordsai_tracing.contexts.span import keywordsai_span_attributes
from openai import OpenAI
from keywordsai_tracing import KeywordsAITelemetry
from keywordsai_tracing.decorators import workflow, task
import os

k_tl = KeywordsAITelemetry()
client = OpenAI()

os.environ["KEYWORDSAI_API_KEY"] = "test"
os.environ["KEYWORDSAI_BASE_URL"] = "https://api.keywordsai.co/api"
os.environ["KEYWORDSAI_API_KEY"] = os.getenv("KEYWORDSAI_API_KEY")

@workflow(name="test_dynamic_attributes")
def test_dynamic_attributes():
    with keywordsai_span_attributes(
        keywordsai_params={
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

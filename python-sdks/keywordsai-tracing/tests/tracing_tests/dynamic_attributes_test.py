from keywordsai_tracing.contexts.span import keywordsai_span_attributes
from openai import OpenAI
from keywordsai_tracing import KeywordsAITelemetry
from keywordsai_tracing.decorators import workflow, task
from dotenv import load_dotenv

load_dotenv(override=True)

k_tl = KeywordsAITelemetry()
client = OpenAI()


@workflow(name="test_dynamic_attributes")
def test_dynamic_attributes():
    with keywordsai_span_attributes(
        keywordsai_params={
            "customer_identifier": "123",
            "customer_email": "test@test.com",
            "customer_name": "John Doe",
            "evaluation_identifier": "456",
            "thread_identifier": "789",
            "custom_identifier": "101",
            "metadata": {"some_key": "some_value"},
        }
    ):
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Hello, world!"}],
        )
    return response

if __name__ == "__main__":
    test_dynamic_attributes()

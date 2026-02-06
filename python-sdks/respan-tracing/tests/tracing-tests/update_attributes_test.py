from dotenv import load_dotenv

load_dotenv(override=True)

import json
from opentelemetry.semconv_ai import SpanAttributes
from keywordsai_tracing import KeywordsAITelemetry
from keywordsai_tracing.decorators import workflow
import os

k_tl = KeywordsAITelemetry()
client = k_tl.get_client()


@workflow(name="update_attributes_test")
def update_attributes_test(input: str):
    force_set_attributes = {
        SpanAttributes.TRACELOOP_ENTITY_INPUT: json.dumps(
            {"args": [], "kwargs": {"text": "hiiiiiii"}}
        ),
        "cost": 100
    }

    client.update_current_span(
        keywordsai_params={
            # keep metadata here if needed
            "metadata": {"test": "test"},
        },
        attributes=force_set_attributes,
        name=f"update_attributes_test",
    )

    some_desired_output = "Some desired output"
    return some_desired_output


if __name__ == "__main__":
    update_attributes_test("Some input")

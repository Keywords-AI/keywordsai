from dotenv import load_dotenv

load_dotenv(override=True)

import json
from opentelemetry.semconv_ai import SpanAttributes
from respan_tracing import RespanTelemetry
from respan_tracing.decorators import workflow
import os

k_tl = RespanTelemetry()
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
        respan_params={
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

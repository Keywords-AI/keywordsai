#!/usr/bin/env python3

from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)


"""
Example demonstrating the new KeywordsAI client API for trace operations.

This example shows how to use the get_client() function and KeywordsAIClient
to interact with the current trace/span context.
"""
import os
# Import the new client API
from keywordsai_tracing import KeywordsAITelemetry, get_client, workflow
from openai import OpenAI

# Initialize telemetry
telemetry = KeywordsAITelemetry(
    app_name="client-example",
    api_key=os.getenv("KEYWORDSAI_API_KEY", "test-key"),
    base_url=os.getenv("KEYWORDSAI_BASE_URL", "https://api.keywordsai.co/api"),
    enabled=True,
)
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@workflow(name="simple_span_updating_example")
def simple_span_updating_example(prompt: str = "Hello, world!"):
    """Main workflow demonstrating span updating"""

    client = get_client()

    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
    )

    # Update span name and add attributes
    client.update_current_span(
        keywordsai_params={"customer_identifier": "updated_customer_id"},
    )

    return response.choices[0].message


if __name__ == "__main__":
    simple_span_updating_example()

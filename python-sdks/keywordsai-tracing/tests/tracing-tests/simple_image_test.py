import time
import json
from dotenv import load_dotenv

load_dotenv(".env", override=True)

from keywordsai_tracing.decorators.base import R
from keywordsai_tracing.main import KeywordsAITelemetry
from keywordsai_tracing.decorators import task
from openai import OpenAI

# Initialize telemetry
telemetry = KeywordsAITelemetry(
    app_name="products-tests",
    log_level="DEBUG",
    is_batching_enabled=False,
)

client = OpenAI()


@task(name="image_analysis")
def image_analysis(prompt: str, image_url: str):
    # Simulate preparing an OpenAI-style messages payload
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": image_url}},
            ],
        },
    ]
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
    )

    return response.choices[0]


def main():
    print("🚀 Running image analysis test...")

    # Run the traced function
    image_analysis(
        "What is in this image?",
        "https://media.istockphoto.com/id/184276818/photo/red-apple.jpg?s=612x612&w=0&k=20&c=NvO-bLsG0DJ_7Ii8SSVoKLurzjmV0Qi4eGfn6nW3l5w=",
    )

    # Allow exporter to run and show debug output
    print("⏳ Waiting for telemetry export...")
    time.sleep(0.2)

    print("✨ Check the output above for debug export preview!")
    print("   Look for lines containing:")
    print("   - '[KeywordsAI Debug] Export preview'")
    print("   - 'image_analysis.task'")
    print("   - 'What is in this image?'")


if __name__ == "__main__":
    main()

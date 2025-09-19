import os
import time
import json

import pytest

os.environ.setdefault("KEYWORDSAI_API_KEY", "test-key")
os.environ.setdefault("KEYWORDSAI_BASE_URL", "http://localhost:4318")

from keywordsai_tracing.main import KeywordsAITelemetry
from keywordsai_tracing.decorators import task


telemetry = KeywordsAITelemetry(
    app_name="products-tests",
    log_level="DEBUG",
    disable_batch=True,
)


@task(name="image_analysis")
def image_analysis(prompt: str, image_url: str):
    # Simulate preparing an OpenAI-style messages payload
    messages = [
        {"role": "user", "content": prompt},
        {"role": "user", "content": json.dumps({"type": "image_url", "url": image_url})},
    ]
    # Simulate a response
    return {"summary": "Detected a cat", "messages": messages}


def test_tracing_image_logs_user_prompt(capfd):
    result = image_analysis("What is in this image?", "https://example.com/cat.png")
    assert result["summary"] == "Detected a cat"

    # Allow exporter to run
    time.sleep(0.2)

    # Capture stdout logs for debug export preview
    out, err = capfd.readouterr()

    # Look for our debug export preview and ensure user message appears
    assert "[KeywordsAI Debug] Export preview" in out or "[KeywordsAI Debug] Export preview" in err
    assert "image_analysis.task" in out or "image_analysis.task" in err
    # Check message keywords present in highlighted attributes
    assert "What is in this image?" in out or "What is in this image?" in err

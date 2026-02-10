"""Integration tests for Respan LiteLLM proxy."""
import os

import dotenv
dotenv.load_dotenv(".env", override=True)

import litellm
import pytest

API_BASE = os.getenv("RESPAN_BASE_URL", "https://api.respan.ai/api")
API_KEY = os.getenv("RESPAN_API_KEY")
MODEL = "gpt-4o-mini"

TOOLS = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get weather for a location",
        "parameters": {
            "type": "object",
            "properties": {"location": {"type": "string"}},
            "required": ["location"],
        },
    },
}]


@pytest.fixture(autouse=True)
def setup():
    """Reset LiteLLM state before/after each test."""
    if not API_KEY:
        pytest.skip("RESPAN_API_KEY not set")
    litellm.success_callback = []
    litellm.failure_callback = []
    yield
    litellm.success_callback = []
    litellm.failure_callback = []


def test_completion():
    """Test basic completion."""
    response = litellm.completion(
        api_key=API_KEY,
        api_base=API_BASE,
        model=MODEL,
        messages=[{"role": "user", "content": "Say hello"}],
    )
    assert response.choices[0].message.content


def test_completion_with_metadata():
    """Test completion with Respan metadata."""
    response = litellm.completion(
        api_key=API_KEY,
        api_base=API_BASE,
        model=MODEL,
        messages=[{"role": "user", "content": "Say hello"}],
        metadata={"respan_params": {"customer_identifier": "test_user"}},
    )
    assert response.choices[0].message.content


def test_streaming():
    """Test streaming completion."""
    response = litellm.completion(
        api_key=API_KEY,
        api_base=API_BASE,
        model=MODEL,
        messages=[{"role": "user", "content": "Say hello"}],
        stream=True,
    )
    chunks = list(response)
    assert len(chunks) > 0


def test_tools():
    """Test completion with tools."""
    response = litellm.completion(
        api_key=API_KEY,
        api_base=API_BASE,
        model=MODEL,
        messages=[{"role": "user", "content": "What's the weather in NYC?"}],
        tools=TOOLS,
        tool_choice={"type": "function", "function": {"name": "get_weather"}},
    )
    msg = response.choices[0].message
    assert msg.tool_calls or msg.content


def test_streaming_with_tools():
    """Test streaming with tools."""
    response = litellm.completion(
        api_key=API_KEY,
        api_base=API_BASE,
        model=MODEL,
        messages=[{"role": "user", "content": "What's the weather in NYC?"}],
        tools=TOOLS,
        tool_choice={"type": "function", "function": {"name": "get_weather"}},
        stream=True,
    )
    chunks = list(response)
    assert len(chunks) > 0

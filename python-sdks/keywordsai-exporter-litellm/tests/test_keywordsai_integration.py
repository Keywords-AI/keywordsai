"""Integration tests for Keywords AI LiteLLM integration.

All tests use Keywords AI API as proxy - no direct OpenAI connection.
"""
import dotenv
dotenv.load_dotenv(".env", override=True)
import os

import litellm
import pytest
from litellm import completion

KEYWORDSAI_API_BASE = os.getenv("KEYWORDSAI_API_BASE")
API_KEY = os.getenv("KEYWORDSAI_API_KEY")
DEFAULT_MODEL = "gpt-4o-mini"

TOOLS = [{
    "type": "function",
    "function": {
        "name": "get_current_weather",
        "description": "Get the current weather in a given location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "The city and state, e.g. San Francisco, CA"},
                "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
            },
            "required": ["location"],
        },
    },
}]

TOOL_CHOICE = {"type": "function", "function": {"name": "get_current_weather"}}


@pytest.fixture
def test_params():
    """Setup common test parameters for proxy tests."""
    if not API_KEY:
        pytest.skip("KEYWORDSAI_API_KEY not set")
    return {
        "model": DEFAULT_MODEL,
        "messages": [{"role": "user", "content": "Say hello in one word"}],
        "tool_messages": [{"role": "user", "content": "Get the current weather in San Francisco, CA"}],
        "metadata": {
            "keywordsai_params": {
                "customer_params": {"customer_identifier": "test_litellm", "email": "test@test.com"},
                "thread_identifier": "test_thread",
                "metadata": {"key": "value"},
            }
        },
    }


@pytest.fixture(autouse=True)
def setup_litellm():
    """Setup LiteLLM to use Keywords AI proxy."""
    litellm.api_base = KEYWORDSAI_API_BASE
    litellm.success_callback = []
    litellm.failure_callback = []
    yield
    litellm.api_base = None
    litellm.success_callback = []
    litellm.failure_callback = []


def test_proxy_completion():
    """Test basic completion through proxy."""
    if not API_KEY:
        pytest.skip("KEYWORDSAI_API_KEY not set")
    response = completion(
        api_key=API_KEY,
        api_base=KEYWORDSAI_API_BASE,
        model=DEFAULT_MODEL,
        messages=[{"role": "user", "content": "Say hello"}],
    )
    assert response.choices[0].message.content is not None


def test_basic_completion(test_params):
    """Test basic completion."""
    response = completion(
        api_key=API_KEY,
        api_base=KEYWORDSAI_API_BASE,
        model=test_params["model"],
        messages=test_params["messages"],
        metadata=test_params["metadata"],
    )
    assert response.choices[0].message.content is not None


def test_streaming_completion(test_params):
    """Test streaming completion."""
    response = completion(
        api_key=API_KEY,
        api_base=KEYWORDSAI_API_BASE,
        model=test_params["model"],
        messages=test_params["messages"],
        metadata=test_params["metadata"],
        stream=True,
    )
    chunks = list(response)
    assert len(chunks) > 0


def test_completion_with_tools(test_params):
    """Test completion with tools."""
    response = completion(
        api_key=API_KEY,
        api_base=KEYWORDSAI_API_BASE,
        model=test_params["model"],
        messages=test_params["tool_messages"],
        tools=TOOLS,
        tool_choice=TOOL_CHOICE,
        metadata=test_params["metadata"],
    )
    message = response.choices[0].message
    assert message.tool_calls is not None or message.content is not None


def test_streaming_with_tools(test_params):
    """Test streaming completion with tools."""
    response = completion(
        api_key=API_KEY,
        api_base=KEYWORDSAI_API_BASE,
        model=test_params["model"],
        messages=test_params["tool_messages"],
        tools=TOOLS,
        tool_choice=TOOL_CHOICE,
        metadata=test_params["metadata"],
        stream=True,
    )
    chunks = list(response)
    assert len(chunks) > 0

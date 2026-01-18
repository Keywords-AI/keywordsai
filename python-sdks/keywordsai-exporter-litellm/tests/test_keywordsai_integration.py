"""Integration tests for Keywords AI LiteLLM integration.

All tests use Keywords AI API as proxy - no direct OpenAI connection.
"""

import os
import pytest
import litellm
from litellm import completion, acompletion

# Constants
KEYWORDSAI_API_BASE = "https://api.keywordsai.co/api/"
DEFAULT_MODEL = "gpt-4o-mini"


@pytest.fixture
def keywordsai_api_key():
    """Get Keywords AI API key from environment."""
    api_key = os.getenv("KEYWORDSAI_API_KEY")
    if not api_key:
        pytest.skip("KEYWORDSAI_API_KEY not set")
    return api_key


@pytest.fixture
def setup_keywordsai(keywordsai_api_key):
    """Setup common test parameters with Keywords AI proxy."""
    return {
        "api_key": keywordsai_api_key,
        "model": DEFAULT_MODEL,
        "messages": [{"role": "user", "content": "Say hello back in one word"}],
        "tool_messages": [{"role": "user", "content": "Get the current weather in San Francisco, CA"}],
        "extra_body": {
            "keywordsai_params": {
                "customer_params": {
                    "customer_identifier": "test_litellm_logging",
                    "email": "test@test.com",
                    "name": "test user"
                },
                "thread_identifier": "test_litellm_thread",
                "metadata": {"key": "value"},
                "evaluation_identifier": "test_litellm_evaluation",
                "prompt_id": "test_litellm_prompt",
            }
        },
        "tools": [{
            "type": "function",
            "function": {
                "name": "get_current_weather",
                "description": "Get the current weather in a given location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA",
                        },
                        "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                    },
                    "required": ["location"],
                },
            },
        }],
        "tool_choice": {"type": "function", "function": {"name": "get_current_weather"}}
    }


@pytest.fixture(autouse=True)
def setup_litellm():
    """Setup LiteLLM to use Keywords AI proxy."""
    litellm.api_base = KEYWORDSAI_API_BASE
    litellm.success_callback = []
    litellm.failure_callback = []
    yield
    # Cleanup
    litellm.api_base = None
    litellm.success_callback = []
    litellm.failure_callback = []


def test_keywordsai_proxy(keywordsai_api_key):
    """Test basic completion through KeywordsAI proxy"""
    response = litellm.completion(
        api_key=keywordsai_api_key,
        model=DEFAULT_MODEL,
        messages=[{"role": "user", "content": "Hi, I am logging from litellm with KeywordsAI!"}]
    )
    
    assert response is not None
    assert response.choices[0].message.content is not None
    print(f"Response: {response.choices[0].message.content}")


def test_basic_completion(setup_keywordsai):
    """Test basic completion without streaming or tools"""
    response = completion(
        api_key=setup_keywordsai["api_key"],
        model=setup_keywordsai["model"], 
        messages=setup_keywordsai["messages"], 
        metadata=setup_keywordsai["extra_body"]
    )
    assert response is not None
    assert response.choices[0].message.content is not None
    print(f"Response: {response.choices[0].message.content}")


def test_streaming_completion(setup_keywordsai):
    """Test streaming completion"""
    response = completion(
        api_key=setup_keywordsai["api_key"],
        model=setup_keywordsai["model"], 
        messages=setup_keywordsai["messages"], 
        metadata=setup_keywordsai["extra_body"],
        stream=True
    )
    chunks = []
    content = []
    for chunk in response:
        chunks.append(chunk)
        if chunk.choices and chunk.choices[0].delta.content:
            content.append(chunk.choices[0].delta.content)
    
    assert len(chunks) > 0
    print(f"Streamed content: {''.join(content)}")


def test_completion_with_tools(setup_keywordsai):
    """Test completion with tools"""
    response = completion(
        api_key=setup_keywordsai["api_key"],
        model=setup_keywordsai["model"],
        messages=setup_keywordsai["tool_messages"],
        tools=setup_keywordsai["tools"],
        tool_choice=setup_keywordsai["tool_choice"],
        metadata=setup_keywordsai["extra_body"]
    )
    assert response is not None
    # Should have tool calls
    message = response.choices[0].message
    assert message.tool_calls is not None or message.content is not None
    print(f"Tool response: {message}")


def test_streaming_completion_with_tools(setup_keywordsai):
    """Test streaming completion with tools"""
    response = completion(
        api_key=setup_keywordsai["api_key"],
        model=setup_keywordsai["model"],
        messages=setup_keywordsai["tool_messages"],
        tools=setup_keywordsai["tools"],
        tool_choice=setup_keywordsai["tool_choice"],
        metadata=setup_keywordsai["extra_body"],
        stream=True
    )
    chunks = [chunk for chunk in response]
    assert len(chunks) > 0
    print(f"Streamed {len(chunks)} chunks with tools")


@pytest.mark.asyncio
async def test_async_completion(setup_keywordsai):
    """Test async completion"""
    response = await acompletion(
        api_key=setup_keywordsai["api_key"],
        model=setup_keywordsai["model"],
        messages=setup_keywordsai["messages"],
        metadata=setup_keywordsai["extra_body"]
    )
    assert response is not None
    assert response.choices[0].message.content is not None
    print(f"Async response: {response.choices[0].message.content}")


@pytest.mark.asyncio
async def test_async_streaming_completion(setup_keywordsai):
    """Test async streaming completion"""
    response = await acompletion(
        api_key=setup_keywordsai["api_key"],
        model=setup_keywordsai["model"],
        messages=setup_keywordsai["messages"],
        metadata=setup_keywordsai["extra_body"],
        stream=True
    )
    chunks = []
    content = []
    async for chunk in response:
        chunks.append(chunk)
        if chunk.choices and chunk.choices[0].delta.content:
            content.append(chunk.choices[0].delta.content)
    
    assert len(chunks) > 0
    print(f"Async streamed content: {''.join(content)}")


@pytest.mark.asyncio
async def test_async_completion_with_tools(setup_keywordsai):
    """Test async completion with tools"""
    response = await acompletion(
        api_key=setup_keywordsai["api_key"],
        model=setup_keywordsai["model"],
        messages=setup_keywordsai["tool_messages"],
        tools=setup_keywordsai["tools"],
        tool_choice=setup_keywordsai["tool_choice"],
        metadata=setup_keywordsai["extra_body"]
    )
    assert response is not None
    message = response.choices[0].message
    assert message.tool_calls is not None or message.content is not None
    print(f"Async tool response: {message}")


@pytest.mark.asyncio
async def test_async_streaming_completion_with_tools(setup_keywordsai):
    """Test async streaming completion with tools"""
    response = await acompletion(
        api_key=setup_keywordsai["api_key"],
        model=setup_keywordsai["model"],
        messages=setup_keywordsai["tool_messages"],
        tools=setup_keywordsai["tools"],
        tool_choice=setup_keywordsai["tool_choice"],
        metadata=setup_keywordsai["extra_body"],
        stream=True
    )
    chunks = []
    async for chunk in response:
        chunks.append(chunk)
    
    assert len(chunks) > 0
    print(f"Async streamed {len(chunks)} chunks with tools")

from tests.test_env import *
from keywordsai_sdk.core import KeywordsAI
from openai import AsyncOpenAI
from openai.types.chat.chat_completion import ChatCompletion
from keywordsai_sdk.integrations.openai import AsyncGenerator

client = AsyncOpenAI()

async def test_stream_generation():
    kai = KeywordsAI()
    try:
        wrapped_creation = kai.async_logging_wrapper(client.chat.completions.create)
        # wrapped_creation = oai_client.chat.completions.create
        response = await wrapped_creation(
            model=test_model,
            messages=test_messages,
            stream=True,
        )
        assert isinstance(response, AsyncGenerator)
        return response
    except Exception as e:
        print(e)

async def test_generation():
    kai = KeywordsAI()
    try:
        wrapped_creation = kai.async_logging_wrapper(client.chat.completions.create, keywordsai_params={
            "customer_identifier": "sdk_customer",
        })
        response = await wrapped_creation(
            model=test_model,
            messages=test_messages,
            stream=False,

        )
        assert isinstance(response, ChatCompletion)
        return response
    except Exception as e:
        assert False, e

import asyncio

async def run_stream():
    response = await test_stream_generation()
    async for chunk in response:
        content = chunk.choices[0].delta.content
        if content:
            print(content, end="")
        pass

if __name__ == "__main__":
    # non streaming
    asyncio.run(test_generation())

    # streaming
    asyncio.run(run_stream())
    KeywordsAI.flush()


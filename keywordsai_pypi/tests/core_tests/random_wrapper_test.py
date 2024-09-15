import sys
sys.path.append(".")
from test_env import *
from keywordsai_sdk.core import KeywordsAI
from keywordsai_sdk.integrations.openai import SyncGenerator
from openai.types.chat.chat_completion import ChatCompletion

# from openai.types.chat.chat_completion_chunk import ChatCompletionChunk


def test_stream_generation():
    kai = KeywordsAI()
    try:
        wrapped_creation = kai.logging_wrapper(oai_client.chat.completions.create)
        # wrapped_creation = oai_client.chat.completions.create
        response = wrapped_creation(
            model=test_model,
            messages=test_messages,
            stream=True,
        )
        assert isinstance(response, SyncGenerator)
        return response
    except Exception as e:
        assert False, e


def test_generation():
    kai = KeywordsAI()
    try:
        wrapped_creation = kai.random_wrapper(oai_client.chat.completions.create, keywordsai_params={
            "customer_identifier": "sdk_customer",
        })
        response = wrapped_creation(
            model=test_model,
            messages=test_messages,
            stream=False,

        )
        assert isinstance(response, ChatCompletion)
        return response
    except Exception as e:
        assert False, e


if __name__ == "__main__":
    # non streaming
    response = test_generation()

    # streaming
    # response = test_stream_generation()
    # Iteration is needed in order to trigger the logging
    # for chunk in response:
    #     content = chunk.choices[0].delta.content
    #     if content:
    #         print(content, end="")
    #     pass
    KeywordsAI.flush()


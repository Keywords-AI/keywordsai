from tests.test_env import *
from keywordsai.decorators import openai_wrapper
from openai import OpenAI

import pytest
client = OpenAI()


def test_openai_wrapper():
    response = openai_wrapper(client.chat.completions.create)(
        messages = [
            {
                "role": "system",
                "content": "You are a chatbot."
            },
            {
                "role": "user",
                "content": "What is your name?"
            }
        ],
        model="gpt-3.5-turbo",
        max_tokens=100,
        stream = True
    )

    assert response is not None

if __name__ == "__main__":
    test_openai_wrapper()
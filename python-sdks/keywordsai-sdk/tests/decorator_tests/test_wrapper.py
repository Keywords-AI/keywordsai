import sys
sys.path.append(".")
from test_env import *
from keywordsai_sdk.core import KeywordsAI
from openai import OpenAI

import pytest
client = OpenAI()

kai = KeywordsAI()

def test_openai_wrapper():
    wrapped_func = kai.logging_wrapper(client.chat.completions.create)
    response = wrapped_func(
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
        stream = False
    )
    
    assert response is not None

if __name__ == "__main__":
    test_openai_wrapper()
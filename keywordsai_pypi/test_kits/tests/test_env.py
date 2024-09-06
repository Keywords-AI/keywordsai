import os
os.environ["KEYWORDS_AI_DEBUG"] = "True"
import logging
from keywordsai.utils.debug_print import *
import openai
import pytest

oai_client = openai.OpenAI()

KEYWORDS_AI_ENDPOINT_LOCAL = os.getenv("KEYWORDS_AI_ENDPOINT_LOCAL")
KEYWORDS_AI_API_KEY_TEST = os.getenv("KEYWORDS_AI_API_KEY_TEST")

kai_local_client = openai.OpenAI(
    api_key=KEYWORDS_AI_API_KEY_TEST, base_url=KEYWORDS_AI_ENDPOINT_LOCAL
)

test_model = "gpt-3.5-turbo"
test_messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hi there!"},
]

from dotenv import load_dotenv
from pathlib import Path
loaded = load_dotenv("./.env", override=True)
import os
import logging
from keywordsai_sdk.utils.debug_print import *
import keywordsai_sdk.keywordsai_config as config
import openai
import pytest
oai_client = openai.OpenAI()
import time

kai_local_client = openai.OpenAI(
    api_key=config.KEYWORDSAI_API_KEY, base_url=config.KEYWORDSAI_BASE_URL
)

print_info(f"ENDPOINT: {config.KEYWORDSAI_BASE_URL}, API_KEY: {config.KEYWORDSAI_API_KEY}")

test_model = "gpt-3.5-turbo"
test_messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hi there!"},
]

test_streaming_messages = [
    {"role": "system", "content": "Streaming test"},
    {"role": "user", "content": "How are you doing today?"},
]

test_mock_response = "Hi, this is a mock response"
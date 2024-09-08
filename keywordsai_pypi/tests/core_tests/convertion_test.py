from tests.test_env import *
from keywordsai_sdk.utils.type_conversion import (
    openai_stream_chunks_to_openai_io,
    openai_io_to_keywordsai_log,
)


stream = True
openai_input = {
        "model": test_model,
        "messages": test_messages,
        "max_tokens": 150,
        "stream": stream,
    }
response = kai_local_client.chat.completions.create(
    **openai_input
)

if stream:
    stream_chunks = list(response)
    response = openai_stream_chunks_to_openai_io(stream_chunks)

log = openai_io_to_keywordsai_log(openai_input=openai_input, openai_output=response)

print(log)

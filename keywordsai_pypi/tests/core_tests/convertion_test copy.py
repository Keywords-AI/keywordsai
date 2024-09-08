from tests.test_env import *
from keywordsai_sdk.utils.type_conversion import (
    openai_stream_chunks_to_openai_io,
    openai_io_to_keywordsai_log,
)

from openai import AsyncOpenAI
client = AsyncOpenAI()
stream = True
openai_input = {
        "model": test_model,
        "messages": test_messages,
        "max_tokens": 150,
        "stream": stream,
    }

async def test_stream_generation():
    response = await client.chat.completions.create(
        **openai_input
    )
    stream_chunks = []
    async for chunk in response:
        stream_chunks.append(chunk)
        
    response = openai_stream_chunks_to_openai_io(stream_chunks)

    log = openai_io_to_keywordsai_log(openai_input=openai_input, openai_output=response)

    print(log)

import asyncio
if __name__ == "__main__":
    asyncio.run(test_stream_generation())
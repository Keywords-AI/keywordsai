# Keywords AI SDK
Keywords AI Python SDK allows you to easily interact with the Keywords AI API.

## Get started
Get started with Keywords AI in minutes
### Installation
#### Users

Poetry
```
poetry add keywordsai
```
Pip
```
pip install keywordsai
```
#### Developers and Contributers
You can install the current directory as a python package via this command
```
poetry install
```
or
```
pip install . -e
```
### Environment Variables
```
touch .env
```
Inside the .env file, you can configure the constants througout the library
```env
DEBUG # Default is "False", set to "True" to enable debug mode for more verbose output
KEYWORDSAI_BASE_URL # Default is "https://api.keywordsai.co/api"
KEYWORDSAI_API_KEY # Your Keywords AI API Key
```
Change values during runtime (not recommended)
```python
import keywordsai.keywordsai_config as config
config.KEYWORDSAI_BASE_URL = "some_url"
```

### Usage

#### Proxy
With Keywords AI as a proxy, observability comes out of box.
```python
from openai import OpenAI
import os
client = OpenAI(
    api_key=os.getenv("KEYWORDSAI_API_KEY"),
    base_url=os.getenv("KEYWORDSAI_BASE_URL")
)

# Use the client to make requests as you would with the OpenAI SDK
```

#### Wrapper (Beta)
Wrap around the OpenAI completion function to automatically log the request and response

Synchronous:
```python
from keywordsai import KeywordsAI
from openai import OpenAI
client = OpenAI()
def test_generation():
    kai = KeywordsAI()
    try:
        wrapped_creation = kai.logging_wrapper(client.chat.completions.create)
        response = wrapped_creation(
            model=test_model,
            messages=test_messages,
            stream=False,
            extra_body={"mock_response": test_mock_response},
        )
        assert isinstance(response, ChatCompletion)
    except Exception as e:
        assert False, e


if __name__ == "__main__":
    generator = test_generation()
``` 

Asynchronous:
```
import sys
sys.path.append(".")
from keywordsai.core import KeywordsAI, AsyncGenerator
from openai import AsyncOpenAI
from openai.types.chat.chat_completion import ChatCompletion

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


```
from openai import OpenAI
from keywordsai_sdk.core import KeywordsAI 
oai_client = OpenAI()
test_model = "gpt-3.5-turbo"
test_messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hi there!"},
]

def test_stream_generation():
    kai = KeywordsAI()
    try:
        wrapped_creation = kai.logging_wrapper(oai_client.chat.completions.create, keywordsai_params={
            "prompt_unit_cost": 0.1,
            "completions_unit_cost": 0.1,
        })
        response = wrapped_creation(
            model=test_model,
            messages=test_messages,
            stream=True,
        )
        return response
    except Exception as e:
        assert False, e


def test_generation():
    kai = KeywordsAI()
    try:
        wrapped_creation = kai.logging_wrapper(oai_client.chat.completions.create, keywordsai_params={
            "customer_identifier": "sdk_customer",
        })
        response = wrapped_creation(
            model=test_model,
            messages=test_messages,
            stream=False,

        )
        return response
    except Exception as e:
        assert False, e


if __name__ == "__main__":
    # non streaming
    # response = test_generation()
    # streaming
    response = test_stream_generation()
    # Iteration is needed in order to trigger the logging
    for chunk in response:
        content = chunk.choices[0].delta.content
        if content:
            print(content, end="")
        pass
    # Short living environment, Flush to ensure all logs are sent
    KeywordsAI.flush()


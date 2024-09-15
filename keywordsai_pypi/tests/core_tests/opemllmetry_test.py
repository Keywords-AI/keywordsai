from tests.test_env import *
from keywordsai_sdk.core import KeywordsAI
import os
from traceloop.sdk.decorators import workflow, task, tool
from openai import OpenAI

kai = KeywordsAI()

@workflow(name="joke_creation")
def create_joke_test():
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Tell me a joke about opentelemetry"}],
    )

    print(completion.choices[0].message.content)
    

if __name__ == "__main__":
    create_joke_test()

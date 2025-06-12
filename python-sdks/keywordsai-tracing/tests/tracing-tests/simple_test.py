from dotenv import load_dotenv

loaded = load_dotenv("./tests/.env", override=True)

# region: setup
import os
from keywordsai_tracing.main import KeywordsAITelemetry

print(os.environ["KEYWORDSAI_BASE_URL"])
print(os.environ["KEYWORDSAI_API_KEY"])
k_tl = KeywordsAITelemetry()
# endregion: setup
import time
from openai import OpenAI
from keywordsai_tracing.decorators import task

client = OpenAI()

@task(name="joke_creation")
def create_joke():
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": "Tell me a joke about opentelemetry"}],
        temperature=0.5,
        max_tokens=100,
        frequency_penalty=0.5,
        presence_penalty=0.5,
        stop=["\n"],
        logprobs=True,
    )
    joke = completion.choices[0].message.content

    return joke

create_joke()

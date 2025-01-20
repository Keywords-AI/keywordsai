"""
Tutorial: Building a Multi-Step LLM Workflow with KeywordsAI Tracing

This tutorial demonstrates how to build a complex workflow using KeywordsAI Tracing,
showing integration with multiple LLM providers and custom functions.
"""

# Step 1: Initialization
# ---------------------
from dotenv import load_dotenv
load_dotenv("./tests/.env", override=True)

import os
from keywordsai_tracing.main import KeywordsAITelemetry
from keywordsai_tracing.decorators import workflow, task
import time

# Initialize KeywordsAI Telemetry
os.environ["KEYWORDSAI_BASE_URL"] = "https://api.keywordsai.co/api"
os.environ["KEYWORDSAI_API_KEY"] = "YOUR_KEYWORDSAI_API_KEY"
k_tl = KeywordsAITelemetry()

# Initialize OpenAI client
from openai import OpenAI
client = OpenAI()

"""
Step 2: First Draft - Basic Workflow
----------------------------------
We'll start by creating a simple workflow that generates a joke, translates it to pirate speak,
and adds a signature. This demonstrates the basic usage of tasks and workflows.

- A task is a single unit of work, decorated with @task
- A workflow is a collection of tasks, decorated with @workflow
- Tasks can be used independently or as part of workflows
"""

@task(name="joke_creation")
def create_joke():
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Tell me a joke about opentelemetry"}],
        temperature=0.5,
        max_tokens=100,
        frequency_penalty=0.5,
        presence_penalty=0.5,
        stop=["\n"],
        logprobs=True,
    )
    return completion.choices[0].message.content

@task(name="signature_generation")
def generate_signature(joke: str):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": "add a signature to the joke:\n\n" + joke}
        ],
    )
    return completion.choices[0].message.content

@task(name="pirate_joke_translation")
def translate_joke_to_pirate(joke: str):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": "translate the joke to pirate language:\n\n" + joke,
            }
        ],
    )
    return completion.choices[0].message.content

@workflow(name="pirate_joke_generator")
def joke_workflow():
    eng_joke = create_joke()
    pirate_joke = translate_joke_to_pirate(eng_joke)
    signature = generate_signature(pirate_joke)
    return pirate_joke + signature

"""
Step 3: Adding Another Workflow
-----------------------------
Let's add audience reactions to make our workflow more complex and demonstrate
how multiple workflows can interact.
"""

@task(name="audience_laughs")
def audience_laughs(joke: str):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": "This joke:\n\n" + joke + " is funny, say hahahahaha",
            }
        ],
        max_tokens=10,
    )
    return completion.choices[0].message.content

@task(name="audience_claps")
def audience_claps():
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Clap once"}],
        max_tokens=5,
    )
    return completion.choices[0].message.content

@task(name="audience_applaud")
def audience_applaud(joke: str):
    clap = audience_claps()
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": "Applaud to the joke, clap clap! " + clap,
            }
        ],
        max_tokens=10,
    )
    return completion.choices[0].message.content

@workflow(name="audience_reaction")
def audience_reaction(joke: str):
    laughter = audience_laughs(joke=joke)
    applauds = audience_applaud(joke=joke)
    return laughter + applauds

"""
Step 4: Adding Vector Storage Capability
-------------------------------------
To demonstrate how to integrate with vector databases and embeddings,
we'll add a store_joke task that generates embeddings for our jokes.
"""

@task(name="store_joke")
def store_joke(joke: str):
    """Simulate storing a joke in a vector database."""
    embedding = client.embeddings.create(
        model="text-embedding-3-small",
        input=joke,
    )
    return embedding.data[0].embedding

# Update create_joke to use store_joke
@task(name="joke_creation")
def create_joke():
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Tell me a joke about opentelemetry"}],
        temperature=0.5,
        max_tokens=100,
        frequency_penalty=0.5,
        presence_penalty=0.5,
        stop=["\n"],
        logprobs=True,
    )
    joke = completion.choices[0].message.content
    store_joke(joke)  # Store the joke's embedding
    return joke

"""
Step 5: Adding Arbitrary Function Calls
------------------------------------
Demonstrate how to trace non-LLM functions by adding a logging task.
"""

@task(name="logging_joke")
def logging_joke(joke: str, reactions: str):
    """Simulates logging the process into a database."""
    print(joke + "\n\n" + reactions)
    time.sleep(1)

"""
Step 6: Adding Different LLM Provider (Anthropic)
---------------------------------------------
Demonstrate compatibility with multiple LLM providers by adding Anthropic integration.
"""

from anthropic import Anthropic
anthropic = Anthropic()

@task(name="ask_for_comments")
def ask_for_comments(joke: str):
    completion = anthropic.messages.create(
        model="claude-3-5-sonnet-20240620",
        messages=[{"role": "user", "content": f"What do you think about this joke: {joke}"}],
        max_tokens=100,
    )
    return completion.content[0].text

@task(name="read_joke_comments")
def read_joke_comments(comments: str):
    return f"Here is the comment from the audience: {comments}"

@workflow(name="audience_interaction")
def audience_interaction(joke: str):
    comments = ask_for_comments(joke=joke)
    read_joke_comments(comments=comments)

"""
Final Step: Combining Everything
-----------------------------
Create a main workflow that combines all the components we've built.
This will create a single trace with multiple workflow spans.
"""

@workflow(name="pirate_joke_plus_audience")
def pirate_joke_plus_audience():
    joke = joke_workflow()  # Basic workflow with joke generation
    reactions = audience_reaction(joke=joke)  # Add audience reactions
    audience_interaction(joke=joke)  # Add Anthropic-powered audience interaction
    logging_joke(joke=joke, reactions=reactions)  # Log everything

# Run the complete workflow
if __name__ == "__main__":
    pirate_joke_plus_audience()
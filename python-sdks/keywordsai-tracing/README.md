# Building an LLM Workflow with KeywordsAI Tracing

This tutorial demonstrates how to build and trace complex LLM workflows using KeywordsAI Tracing. We'll create an example that generates jokes, translates them to pirate language, and simulates audience reactions - all while capturing detailed telemetry of our LLM calls.

## Prerequisites

- Python 3.7+
- OpenAI API key
- Anthropic API key
- Keywords AI API key, you can get your API key from the [API keys page](https://platform.keywordsai.co/platform/api/api-keys)

## Installation
```bash
pip install keywordsai-tracing openai anthropic
```


## Tutorial

### Step 1: Initialization
```
import os
from keywordsai_tracing.main import KeywordsAITelemetry
from keywordsai_tracing.decorators import workflow, task
import time

# Initialize KeywordsAI Telemetry
os.environ["KEYWORDSAI_API_KEY"] = "YOUR_KEYWORDSAI_API_KEY"
k_tl = KeywordsAITelemetry()

# Initialize OpenAI client
from openai import OpenAI
client = OpenAI()
```


### Step 2: First Draft - Basic Workflow
We'll start by creating a simple workflow that generates a joke, translates it to pirate speak,
and adds a signature. This demonstrates the basic usage of tasks and workflows.

- A task is a single unit of work, decorated with `@task`
- A workflow is a collection of tasks, decorated with `@workflow`
- Tasks can be used independently or as part of workflows

```python
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

if __name__ == "__main__":
    joke_workflow()
```

Run the workflow and see the trace in Keywords AI `Traces` tab.

### Step 3: Adding Another Workflow
Let's add audience reactions to make our workflow more complex and demonstrate
what multiple workflow traces look like.

```python
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


@workflow(name="joke_and_audience_reaction") #<--------- Create the new workflow that combines both workflows together
def joke_and_audience_reaction():
    pirate_joke = joke_workflow()
    reactions = audience_reaction(pirate_joke)
```

Don't forget to update the entrypoint!
```python
if __name__ == "__main__":
    joke_and_audience_reaction() # <--------- Update the entrypoint here
```

Run the workflow again and see the trace in Keywords AI `Traces` tab, notice the new span for the `audience_reaction` workflow in parallel with the `joke_workflow`. Congratulation! You have created a trace with multiple workflows.

### Step 4: Adding Vector Storage Capability
To demonstrate how to integrate with vector databases and embeddings,
we'll add a store_joke task that generates embeddings for our jokes.

```python
@task(name="store_joke")
def store_joke(joke: str):
    """Simulate storing a joke in a vector database."""
    embedding = client.embeddings.create(
        model="text-embedding-3-small",
        input=joke,
    )
    return embedding.data[0].embedding
```

Update create_joke to use store_joke
```python
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
    store_joke(joke)  # <--------- Add the task here
    return joke
```
Run the workflow again and see the trace in Keywords AI `Traces` tab, notice the new span for the `store_joke` task.

Expanding the `store_joke` task, you can see the embeddings call is recognized as `openai.embeddings`.

### Step 5: Adding Arbitrary Function Calls
Demonstrate how to trace non-LLM functions by adding a logging task.

```python
@task(name="logging_joke")
def logging_joke(joke: str, reactions: str):
    """Simulates logging the process into a database."""
    print(joke + "\n\n" + reactions)
    time.sleep(1)
```

Update `joke_and_audience_reaction`
```python
@workflow(name="joke_and_audience_reaction")
def joke_and_audience_reaction():
    pirate_joke = joke_workflow()
    reactions = audience_reaction(pirate_joke)
    logging_joke(pirate_joke, reactions) # <-------- Add this workflow here
```

Run the workflow again and see the trace in Keywords AI `Traces` tab, notice the new span for the `logging_joke` task.

This is a simple example of how to trace arbitrary functions. You can see the all the inputs and outputs of `logging_joke` task.

### Step 6: Adding Different LLM Provider (Anthropic)

Demonstrate compatibility with multiple LLM providers by adding Anthropic integration.

```python
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
```

Update `joke_and_audience_reaction`
```python
@workflow(name="joke_and_audience_reaction")
def joke_and_audience_reaction():
    pirate_joke = joke_workflow()
    reactions = audience_reaction(pirate_joke)
    audience_interaction(pirate_joke) # <-------- Add this workflow here
    logging_joke(pirate_joke, reactions)
```

Running the workflow for one last time, you can see that the new `audience_interaction` can recognize the `anthropic.completion` calls.

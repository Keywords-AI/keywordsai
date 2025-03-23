<p align="center">
<a href="https://www.keywordsai.co#gh-light-mode-only">
<img width="800" src="https://keywordsai-static.s3.us-east-1.amazonaws.com/social_media_images/logo-header.jpg">
</a>
<a href="https://www.keywordsai.co#gh-dark-mode-only">
<img width="800" src="https://keywordsai-static.s3.us-east-1.amazonaws.com/social_media_images/logo-header-dark.jpg">
</a>
</p>
<p align="center">
  <p align="center">Observability, prompt management, and evals for LLM engineering teams.</p>
</p>

<div align="center">
  <a href="https://www.ycombinator.com/companies/keywords-ai"><img src="https://img.shields.io/badge/Y%20Combinator-W24-orange" alt="Y Combinator W24"></a>
  <a href="https://www.keywordsai.co"><img src="https://img.shields.io/badge/Platform-green.svg?style=flat-square" alt="Platform" style="height: 20px;"></a>
  <a href="https://docs.keywordsai.co/get-started/overview"><img src="https://img.shields.io/badge/Documentation-blue.svg?style=flat-square" alt="Documentation" style="height: 20px;"></a>
  <a href="https://x.com/keywordsai/"><img src="https://img.shields.io/twitter/follow/keywordsai?style=social" alt="Twitter" style="height: 20px;"></a>
  <a href="https://discord.com/invite/KEanfAafQQ"><img src="https://img.shields.io/badge/discord-7289da.svg?style=flat-square&logo=discord" alt="Discord" style="height: 20px;"></a>

</div>

# Keywords AI Tracing
<div align="center">
<img src="https://keywordsai-static.s3.us-east-1.amazonaws.com/social_media_images/github-cover.jpg" width="800"></img>
</div>
Keywords AI's library for sending telemetries of LLM applications in [OpenLLMetry](https://github.com/traceloop/openllmetry) format.


## Integrations
<div align="center" style="background-color: white; padding: 20px; border-radius: 10px; margin: 0 auto; max-width: 800px;">
  <div style="display: flex; flex-wrap: wrap; justify-content: center; align-items: center; gap: 120px; margin-bottom: 20px;">
    <a href="https://docs.keywordsai.co/features/monitoring/traces/integrations/openai-agents-sdk"><img src="https://keywordsai-static.s3.us-east-1.amazonaws.com/github/openai-agents-sdk.jpg" height="45" alt="OpenAI Agents SDK"></a>
        <a href="https://docs.keywordsai.co/features/monitoring/traces/integrations/langgraph"><img src="https://keywordsai-static.s3.us-east-1.amazonaws.com/github/langgraph.jpg" height="45" alt="LangGraph"></a>
    <a href="https://docs.keywordsai.co/features/monitoring/traces/integrations/vercel-ai-sdk"><img src="https://keywordsai-static.s3.us-east-1.amazonaws.com/github/vercel.jpg" height="45" alt="Vercel AI SDK"></a>
  </div>

</div>


## Quickstart

### 1️⃣ Get an API key
Go to Keywords AI platform and [get your API key](https://platform.keywordsai.co/platform/api/api-keys).

### 2️⃣ Download package

#### Python

```bash
pip install keywordsai-tracing
```

#### TypeScript/JavaScript

```bash
npm install @keywordsai/tracing
```


### 3️⃣ Initialize Keywords AI tracing processor
#### Python
```python
import os
from keywordsai_tracing.main import KeywordsAITelemetry

os.environ["KEYWORDSAI_BASE_URL"] = "https://api.keywordsai.co/api" # This is also the default value if not explicitly set
os.environ["KEYWORDSAI_API_KEY"] = "YOUR_KEYWORDSAI_API_KEY"
k_tl = KeywordsAITelemetry()
```

#### Typescript/JavaScript
```TypeScript
import { KeywordsAITelemetry } from '@keywordsai/tracing';

// Initialize clients
// Make sure to set these environment variables or pass them directly
const keywordsAI = new KeywordsAITelemetry({
    apiKey: process.env.KEYWORDSAI_API_KEY || "",
    baseUrl: process.env.KEYWORDSAI_BASE_URL || "",
    appName: 'test-app',
    disableBatch: true  // For testing, disable batching
});
```

### 4️⃣ Trace agent workflows and tasks

#### Python
You can now trace your LLM applications using the decorators.
> A workflow is the whole process of an AI agent run, and a workflow may contains several tasks also could say tools/LLM calls.
>
> In the example, below, this means there's an Agent run named `my_workflow` and it contains 1 task `my_task` in this agent.
```python
from keywordsai_tracing.decorators import workflow, task

@workflow(name="my_workflow")
def my_workflow():
    @task(name="my_task")
    def my_task():
        pass
    my_task()
```


#### Typescript/JavaScript
You can now trace your LLM applications by wrapping the wrappers around your functions (`keywordsAI.withTask` in the below example)

> A workflow is the whole process of an AI agent run, and a workflow may contains several tasks also could say tools/LLM calls.
>
> In the example, below, this means there's an Agent run named `pirate_joke_workflow` and it contains 1 task `joke_creation` in this agent.
```TypeScript
async function createJoke() {
    return await keywordsAI.withTask(
        { name: 'joke_creation' },
        async () => {
            const completion = await openai.chat.completions.create({
                messages: [{ role: 'user', content: 'Tell me a joke about TypeScript' }],
                model: 'gpt-3.5-turbo',
                temperature: 0.7
            });
            return completion.choices[0].message.content;
        }
    );
}

async function jokeWorkflow() {
    return await keywordsAi.withWorkflow(
        { name: 'pirate_joke_workflow' },
        async () => {
            const joke = await createJoke();
            return joke;
        }
    );
}
```

### 5️⃣ See traces in [Keywords AI](https://www.keywordsai.co)
<div align="center">
<img src="https://keywordsai-static.s3.us-east-1.amazonaws.com/github/traces-output.png" width="800"> </img>
</div>

## ⭐️ Star us 🙏
Please star us if you found this is helpful!


------------------
For a **comprehensive example**, see the [trace example run](https://github.com/Keywords-AI/keywordsai_sdks/blob/main/python-sdks/keywordsai-tracing/tests/tracing_tests/basic_workflow_test.py).
**Step by step guide** can be below:  
- [Python](https://github.com/Keywords-AI/keywordsai_sdks/blob/main/python-sdks/keywordsai-tracing/README.md).
- [TypeScript](https://github.com/Keywords-AI/keywordsai/blob/main/javascript-sdks/keywordsai-js/README.md).

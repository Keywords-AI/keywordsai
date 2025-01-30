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

# Keywords AI

Observability, prompt management, and evals for LLM engineering teams.

## Keywords AI Tracing
Keywords AI's library for sending telemetries of LLM applications in [OpenLLMetry](https://github.com/traceloop/openllmetry) format.

### Installation

#### Python
<details>
<summary>pip</summary>

```bash
pip install keywordsai-tracing
```
</details>

<details>
<summary>poetry</summary>

```bash
poetry add keywordsai-tracing
```
</details>

#### TypeScript/JavaScript
<details>
<summary>npm</summary>

```bash
npm install @keywordsai/tracing
```
</details>

<details>
<summary>yarn</summary>

```bash
yarn add @keywordsai/tracing
```
</details>

### Getting started

#### Python
```python
import os
from keywordsai_tracing.main import KeywordsAITelemetry

os.environ["KEYWORDSAI_BASE_URL"] = "https://api.keywordsai.co/api" # This is also the default value if not explicitly set
os.environ["KEYWORDSAI_API_KEY"] = "YOUR_KEYWORDSAI_API_KEY"
k_tl = KeywordsAITelemetry()
```
That's it! You can now trace your LLM applications using the decorators.
```python
from keywordsai_tracing.decorators import workflow, task

@workflow(name="my_workflow")
def my_workflow():
    @task(name="my_task")
    def my_task():
        pass
    my_task()
```
For a **comprehensive example**, see the [trace example run](https://github.com/Keywords-AI/keywordsai_sdks/blob/main/python-sdks/keywordsai-tracing/tests/tracing_tests/basic_workflow_test.py).

#### TypeScript
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
That's it! You can now trace your LLM applications by wrapping the wrappers around your functions (`keywordsAI.withTask` in the below example)
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
```
**Step by step guide** can be below:  
- [Python](https://github.com/Keywords-AI/keywordsai_sdks/blob/main/python-sdks/keywordsai-tracing/README.md).
- [TypeScript](https://github.com/Keywords-AI/keywordsai/blob/main/javascript-sdks/keywordsai-js/README.md).

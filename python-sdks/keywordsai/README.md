# Keywords AI Python SDK

A comprehensive Python SDK for Keywords AI monitoring, evaluation, and analytics APIs. Build, test, and evaluate your AI applications with ease.

## 🚀 Features

- **📊 Dataset Management** - Create, manage, and analyze datasets from your AI logs
- **🔬 Experiment Framework** - Run A/B tests with different prompts and model configurations
- **📈 AI Evaluation** - Evaluate model outputs with built-in and custom evaluators
- **📝 Log Management** - Comprehensive logging and monitoring for AI applications

## 📦 Installation

```bash
pip install keywordsai
```

Or with Poetry:

```bash
poetry add keywordsai
```

## 🔑 Quick Start

### 1. Set up your API key

```bash
export KEYWORDSAI_API_KEY="your-api-key-here"
```

Or create a `.env` file:

```env
KEYWORDSAI_API_KEY=your-api-key-here
KEYWORDSAI_BASE_URL=https://api.keywordsai.co  # optional
```

### 2. Basic Usage

```python
from keywordsai import DatasetAPI, ExperimentAPI, EvaluatorAPI

# Initialize clients
dataset_client = DatasetAPI(api_key="your-api-key")
experiment_client = ExperimentAPI(api_key="your-api-key")
evaluator_client = EvaluatorAPI(api_key="your-api-key")

# Create a dataset from logs
dataset = dataset_client.create({
    "name": "My Dataset",
    "description": "Dataset for evaluation",
    "type": "sampling",
    "sampling": 100
})

# List available evaluators
evaluators = evaluator_client.list()
print(f"Available evaluators: {len(evaluators.results)}")

# Run evaluation
evaluation = dataset_client.run_dataset_evaluation(
    dataset_id=dataset.id,
    evaluator_slugs=["accuracy-evaluator", "relevance-evaluator"]
)
```

## 🏗️ Core APIs

### Dataset API
Manage datasets and run evaluations on your AI model outputs:

```python
from keywordsai import DatasetAPI, DatasetCreate

client = DatasetAPI(api_key="your-api-key")

# Create dataset
dataset = client.create(DatasetCreate(
    name="Production Logs",
    type="sampling",
    sampling=1000
))

# Add logs to dataset
client.add_logs_to_dataset(
    dataset_id=dataset.id,
    start_time="2024-01-01T00:00:00Z",
    end_time="2024-01-02T00:00:00Z"
)

# Run evaluations
evaluation = client.run_dataset_evaluation(
    dataset_id=dataset.id,
    evaluator_slugs=["accuracy-evaluator"]
)
```

### Experiment API
Run A/B tests with different model configurations:

```python
from keywordsai import ExperimentAPI, ExperimentCreate, ExperimentColumnType

client = ExperimentAPI(api_key="your-api-key")

# Create experiment
experiment = client.create(ExperimentCreate(
    name="Prompt A/B Test",
    description="Testing different system prompts",
    columns=[
        ExperimentColumnType(
            name="Version A",
            model="gpt-4",
            temperature=0.7,
            prompt_messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "{{user_input}}"}
            ]
        ),
        ExperimentColumnType(
            name="Version B", 
            model="gpt-4",
            temperature=0.3,
            prompt_messages=[
                {"role": "system", "content": "You are a concise assistant."},
                {"role": "user", "content": "{{user_input}}"}
            ]
        )
    ]
))

# Run experiment
results = client.run_experiment(experiment_id=experiment.id)
```

### Evaluator API
Discover and use AI evaluators:

```python
from keywordsai import EvaluatorAPI

client = EvaluatorAPI(api_key="your-api-key")

# List all evaluators
evaluators = client.list()

# Get specific evaluator details
evaluator = client.get("accuracy-evaluator")
print(f"Evaluator: {evaluator.name}")
print(f"Description: {evaluator.description}")
```

### Prompt API
Manage prompts and their versions:

```python
from keywordsai import PromptAPI
from keywordsai_sdk.keywordsai_types.prompt_types import Prompt, PromptVersion

client = PromptAPI(api_key="your-api-key")

# Create a prompt
prompt = client.create()

# Create a version for the prompt
version = client.create_version(prompt.id, PromptVersion(
    prompt_version_id="v1",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ],
    model="gpt-4o-mini",
    temperature=0.7
))

# List all prompts
prompts = client.list()

# Get specific prompt with versions
prompt_details = client.get(prompt.id)
```

### Log API
Create and manage AI application logs:

```python
from keywordsai import LogAPI, KeywordsAILogParams

client = LogAPI(api_key="your-api-key")

# Create log entry
log = client.create(KeywordsAILogParams(
    model="gpt-4",
    input="What is machine learning?",
    output="Machine learning is a subset of AI...",
    status_code=200,
    prompt_tokens=10,
    completion_tokens=50
))
```

## 🔄 Async Support

All APIs support both synchronous and asynchronous operations:

```python
import asyncio
from keywordsai import DatasetAPI

async def main():
    client = DatasetAPI(api_key="your-api-key")
    
    # Use 'await' with 'a' prefixed methods for async
    datasets = await client.alist()
    dataset = await client.aget(dataset_id="123")
    
    print(f"Found {datasets.count} datasets")

asyncio.run(main())
```

## 📚 Examples

Check out the [`examples/`](https://github.com/Keywords-AI/keywordsai/tree/main/python-sdks/keywordsai/examples) directory for complete workflows:

- **[Simple Evaluator Example](https://github.com/Keywords-AI/keywordsai/blob/main/python-sdks/keywordsai/examples/simple_evaluator_example.py)** - Basic evaluator operations
- **[Dataset Workflow](https://github.com/Keywords-AI/keywordsai/blob/main/python-sdks/keywordsai/examples/dataset_workflow_example.py)** - Complete dataset management
- **[Experiment Workflow](https://github.com/Keywords-AI/keywordsai/blob/main/python-sdks/keywordsai/examples/experiment_workflow_example.py)** - A/B testing with experiments
- **[Prompt Workflow](https://github.com/Keywords-AI/keywordsai/blob/main/python-sdks/keywordsai/examples/prompt_workflow_example.py)** - Prompt and version management

```bash
# Run examples
python examples/simple_evaluator_example.py
python examples/dataset_workflow_example.py
python examples/experiment_workflow_example.py
python examples/prompt_workflow_example.py
```

## 🧪 Testing

The SDK includes comprehensive tests for both unit testing and real API integration:

```bash
# Install development dependencies
poetry install

# Run all tests
python -m pytest tests/ -v

# Run specific test suites
python -m pytest tests/test_dataset_api_real.py -v
python -m pytest tests/test_experiment_api_real.py -v
```

## 📖 API Reference

### Core Classes

- **`DatasetAPI`** - Dataset management and evaluation
- **`ExperimentAPI`** - A/B testing and experimentation  
- **`EvaluatorAPI`** - AI model evaluation tools
- **`LogAPI`** - Application logging and monitoring
- **`PromptAPI`** - Prompt and version management

### Type Safety

All APIs include comprehensive type definitions:

```python
from keywordsai import (
    Dataset, DatasetCreate, DatasetUpdate,
    Experiment, ExperimentCreate, ExperimentUpdate,
    Evaluator, EvaluatorList,
    KeywordsAILogParams, LogList,
    PromptAPI
)
from keywordsai_sdk.keywordsai_types.prompt_types import (
    Prompt, PromptVersion
)
```

## 🔧 Configuration

### Environment Variables

```bash
KEYWORDSAI_API_KEY=your-api-key-here          # Required
KEYWORDSAI_BASE_URL=https://api.keywordsai.co # Optional
```

### Client Initialization

```python
# Using environment variables
dataset_client = DatasetAPI()  # Reads from KEYWORDSAI_API_KEY
prompt_client = PromptAPI()    # Reads from KEYWORDSAI_API_KEY

# Explicit configuration
client = DatasetAPI(
    api_key="your-api-key",
    base_url="https://api.keywordsai.co"
)
```

## 📋 Requirements

- Python 3.9+
- httpx >= 0.25.0
- keywordsai-sdk >= 0.4.63

## 📄 License

Apache 2.0 - see [LICENSE](https://github.com/Keywords-AI/keywordsai/blob/main/LICENSE) for details.

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](https://github.com/Keywords-AI/keywordsai/blob/main/CONTRIBUTING.md) for details.

## 📞 Support

- 📧 Email: [team@keywordsai.co](mailto:team@keywordsai.co)
- 📖 Documentation: [https://docs.keywordsai.co](https://docs.keywordsai.co)
- 🐛 Issues: [GitHub Issues](https://github.com/Keywords-AI/keywordsai/issues)

---

Built with ❤️ by the Keywords AI team

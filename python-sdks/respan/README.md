# Respan Python SDK

**[respan.ai](https://respan.ai)** | **[Documentation](https://docs.respan.ai)** | **[PyPI](https://pypi.org/project/respan-ai/)**

A comprehensive Python SDK for Respan monitoring, evaluation, and analytics APIs. Build, test, and evaluate your AI applications with ease.

## 🚀 Features

- **📊 Dataset Management** - Create, manage, and analyze datasets from your AI logs
- **🔬 Experiment Framework** - Run A/B tests with different prompts and model configurations
- **📈 AI Evaluation** - Evaluate model outputs with built-in and custom evaluators
- **📝 Log Management** - Comprehensive logging and monitoring for AI applications

## 📦 Installation

```bash
pip install respan
```

Or with Poetry:

```bash
poetry add respan
```

## 🔑 Quick Start

### 1. Set up your API key

```bash
export RESPAN_API_KEY="your-api-key-here"
```

Or create a `.env` file:

```env
RESPAN_API_KEY=your-api-key-here
RESPAN_BASE_URL=https://api.respan.ai  # optional
```

### 2. Basic Usage

```python
from respan import DatasetAPI, ExperimentAPI, EvaluatorAPI

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
from respan import DatasetAPI, DatasetCreate

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
from respan import ExperimentAPI, ExperimentCreate, ExperimentColumnType

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
from respan import EvaluatorAPI

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
from respan import PromptAPI
from respan_sdk.respan_types.prompt_types import Prompt, PromptVersion

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
from respan import LogAPI, RespanLogParams

client = LogAPI(api_key="your-api-key")

# Create log entry
log = client.create(RespanLogParams(
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
from respan import DatasetAPI

async def main():
    client = DatasetAPI(api_key="your-api-key")
    
    # Use 'await' with 'a' prefixed methods for async
    datasets = await client.alist()
    dataset = await client.aget(dataset_id="123")
    
    print(f"Found {datasets.count} datasets")

asyncio.run(main())
```

## 📚 Examples

Check out the [`examples/`](https://github.com/Repsan/respan/tree/main/python-sdks/respan/examples) directory for complete workflows:

- **[Simple Evaluator Example](https://github.com/Repsan/respan/blob/main/python-sdks/respan/examples/simple_evaluator_example.py)** - Basic evaluator operations
- **[Dataset Workflow](https://github.com/Repsan/respan/blob/main/python-sdks/respan/examples/dataset_workflow_example.py)** - Complete dataset management
- **[Experiment Workflow](https://github.com/Repsan/respan/blob/main/python-sdks/respan/examples/experiment_workflow_example.py)** - A/B testing with experiments
- **[Prompt Workflow](https://github.com/Repsan/respan/blob/main/python-sdks/respan/examples/prompt_workflow_example.py)** - Prompt and version management

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
from respan import (
    Dataset, DatasetCreate, DatasetUpdate,
    Experiment, ExperimentCreate, ExperimentUpdate,
    Evaluator, EvaluatorList,
    RespanLogParams, LogList,
    PromptAPI
)
from respan_sdk.respan_types.prompt_types import (
    Prompt, PromptVersion
)
```

## 🔧 Configuration

### Environment Variables

```bash
RESPAN_API_KEY=your-api-key-here          # Required
RESPAN_BASE_URL=https://api.respan.ai # Optional
```

### Client Initialization

```python
# Using environment variables
dataset_client = DatasetAPI()  # Reads from RESPAN_API_KEY
prompt_client = PromptAPI()    # Reads from RESPAN_API_KEY

# Explicit configuration
client = DatasetAPI(
    api_key="your-api-key",
    base_url="https://api.respan.ai"
)
```

## 📋 Requirements

- Python 3.9+
- httpx >= 0.25.0
- respan-sdk >= 0.4.63

## 📄 License

Apache 2.0 - see [LICENSE](https://github.com/Repsan/respan/blob/main/LICENSE) for details.

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](https://github.com/Repsan/respan/blob/main/CONTRIBUTING.md) for details.

## 📞 Support

- 📧 Email: [team@respan.ai](mailto:team@respan.ai)
- 📖 Documentation: [https://docs.respan.ai](https://docs.respan.ai)
- 🐛 Issues: [GitHub Issues](https://github.com/Repsan/respan/issues)

---

Built with ❤️ by the Respan team

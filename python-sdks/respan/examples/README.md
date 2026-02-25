# Respan SDK Examples

This directory contains clean, readable examples showing how to use the Respan Python SDK.

## Available Examples

### 🔍 **Simple Evaluator Example** (`simple_evaluator_example.py`)
Shows basic evaluator operations:
- List available evaluators
- Get evaluator details
- Explore evaluator attributes

```bash
python examples/simple_evaluator_example.py
```

### 📊 **Complete Dataset Workflow** (`dataset_workflow_example.py`)
Demonstrates the full dataset management workflow:
- List logs
- Create datasets
- Add/manage logs in datasets
- Run evaluations
- Get results

```bash
python examples/dataset_workflow_example.py
```

### 🔬 **Experiment Workflow** (`experiment_workflow_example.py`)
Shows comprehensive experiment management:
- Create experiments with columns and rows
- Add test cases and model configurations
- Run experiments to generate outputs
- Run evaluations on results
- Both async and sync examples

```bash
python examples/experiment_workflow_example.py
```

### 📝 **Prompt Workflow** (`prompt_workflow_example.py`)
Demonstrates complete prompt management workflow:
- Create and update prompts
- Create versions with different configurations
- List and retrieve prompts and versions
- Update prompt and version properties
- Both async and sync examples

```bash
python examples/prompt_workflow_example.py
```

### 🔧 **Flexible Input** (`flexible_input_example.py`)
Shows flexible input options across all APIs:
- Use dictionaries instead of Pydantic models
- Simplified API usage patterns
- Cross-API examples

```bash
python examples/flexible_input_example.py
```

### 📊 **Logs Operations** (`logs_operation_example.py`)
Basic log operations example:
- List available logs
- Simple log API usage

```bash
python examples/logs_operation_example.py
```

### 🏗️ **SDK Structure Demo** (`sdk_structure_demo.py`)
Shows SDK structure and initialization:
- Available API clients overview
- Client initialization patterns
- SDK architecture demonstration

```bash
python examples/sdk_structure_demo.py
```

## Quick Start

1. **Set up environment variables**:
   ```bash
   # Create .env file in project root
   RESPAN_API_KEY=your_api_key_here
   RESPAN_BASE_URL=http://localhost:8000  # optional
   ```

2. **Install dependencies**:
   ```bash
   poetry install
   ```

3. **Run an example**:
   ```bash
   python examples/simple_evaluator_example.py
   ```

## Example vs Test Files

| Purpose | Location | When to Use |
|---------|----------|-------------|
| **Examples** | `examples/` | Learning the SDK, copy-paste code, demos |
| **Tests** | `tests/` | Validation, CI/CD, ensuring SDK works correctly |

### Examples are for:
- 📚 Learning how to use the SDK
- 🎯 Quick copy-paste code snippets  
- 🎪 Demos and presentations
- 📖 Documentation and tutorials

### Tests are for:
- ✅ Ensuring code correctness
- 🔄 CI/CD pipelines
- 🐛 Catching regressions
- 📊 Code coverage metrics

## Running Examples vs Tests

```bash
# Run clean, readable examples
python examples/dataset_workflow_example.py

# Run robust test suites  
python -m pytest tests/test_respan_api_integration.py -v -s

# Hybrid: Demo mode from integration test file
python tests/test_respan_api_integration.py

# Test mode from integration test file
python tests/test_respan_api_integration.py --test
```

## Best Practices

1. **Examples should be**:
   - ✅ Clean and readable
   - ✅ Well-commented
   - ✅ Focused on one main workflow
   - ✅ Easy to copy-paste
   - ✅ Minimal error handling (just enough)

2. **Tests should be**:
   - ✅ Comprehensive error handling
   - ✅ Proper cleanup (finally blocks)
   - ✅ Assertions for validation
   - ✅ Isolated and repeatable
   - ✅ Good coverage of edge cases

This separation keeps examples clean while maintaining robust testing! 🚀
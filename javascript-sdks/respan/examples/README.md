# Respan SDK Examples

This directory contains clean, readable examples showing how to use the Respan TypeScript/JavaScript SDK.

## Available Examples

### 🔍 **Simple Evaluator Example** (`simple-evaluator-example.ts`)
Shows basic evaluator operations:
- List available evaluators
- Get evaluator details
- Explore evaluator attributes

```bash
npx tsx examples/simple-evaluator-example.ts
```

### 📊 **Complete Dataset Workflow** (`dataset-workflow-example.ts`)
Demonstrates the full dataset management workflow:
- List logs
- Create datasets
- Add/manage logs in datasets
- Run evaluations
- Get results

```bash
npx tsx examples/dataset-workflow-example.ts
```

### 🔬 **Experiment Workflow** (`experiment-workflow-example.ts`)
Shows comprehensive experiment management:
- Create experiments with columns and rows
- Add test cases and model configurations
- Run experiments to generate outputs
- Run evaluations on results
- Async examples with proper error handling

```bash
npx tsx examples/experiment-workflow-example.ts
```

### 🔧 **Flexible Input** (`flexible-input-example.ts`)
Shows flexible input options across all APIs:
- Use plain objects instead of complex types
- Simplified API usage patterns
- Cross-API examples

```bash
npx tsx examples/flexible-input-example.ts
```

### 📊 **Logs Operations** (`logs-operation-example.ts`)
Basic log operations example:
- List available logs
- Simple log API usage

```bash
npx tsx examples/logs-operation-example.ts
```

### 🏗️ **SDK Structure Demo** (`sdk-structure-demo.ts`)
Shows SDK structure and initialization:
- Available API clients overview
- Client initialization patterns
- SDK architecture demonstration

```bash
npx tsx examples/sdk-structure-demo.ts
```

## Quick Start

1. **Install dependencies**:
   ```bash
   npm install
   # or
   yarn install
   ```

2. **Set up environment variables**:
   ```bash
   # Create .env file in project root
   echo "RESPAN_API_KEY=your_api_key_here
   RESPAN_BASE_URL=http://localhost:8000" > .env
   
   # Or copy from example and edit
   cp .env.example .env
   # Then edit .env with your actual values
   ```

3. **Build the SDK**:
   ```bash
   npm run build
   ```

4. **Run an example**:
   ```bash
   npm run example:simple-evaluator
   # or directly:
   npx tsx examples/simple-evaluator-example.ts
   # or build first, then:
   node dist/examples/simple-evaluator-example.js
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
npx tsx examples/dataset-workflow-example.ts

# Run built examples  
npm run build && node dist/examples/dataset-workflow-example.js

# Run all examples in sequence
npm run examples

# Run tests (when available)
npm test
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
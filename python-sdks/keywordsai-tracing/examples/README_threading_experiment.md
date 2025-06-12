# Threading and Context Propagation Experiment

This experiment demonstrates how global variables, Python context variables, and OpenTelemetry context behave in multi-threaded environments.

## What This Experiment Tests

### 🔬 Experiment 1: Global Variables in Threads
- **Purpose**: Show how global variables behave when modified by multiple threads
- **Expected Result**: Race conditions and data corruption
- **Key Learning**: Global variables are NOT thread-safe

### 🔬 Experiment 2: Context Variables in Threads  
- **Purpose**: Demonstrate Python's `contextvars` behavior across threads
- **Expected Result**: Each thread has isolated context
- **Key Learning**: Context variables provide thread-local storage

### 🔬 Experiment 3: OpenTelemetry Context in Threads
- **Purpose**: Test if OpenTelemetry context automatically propagates to new threads
- **Expected Result**: Context does NOT propagate automatically
- **Key Learning**: Each thread starts with empty OpenTelemetry context

### 🔬 Experiment 4: Manual Context Propagation
- **Purpose**: Show how to manually propagate OpenTelemetry context
- **Expected Result**: Manual propagation works correctly
- **Key Learning**: Use `context.attach()/detach()` for distributed tracing

### 🔬 Experiment 5: ThreadPoolExecutor Context Behavior
- **Purpose**: Test context behavior with thread pools
- **Expected Result**: Regular usage loses context, manual propagation preserves it
- **Key Learning**: Thread pools require explicit context management

## How to Run

### Option 1: Direct Execution
```bash
cd examples
python threading_context_experiment.py
```

### Option 2: Using the Runner Script
```bash
cd examples
python run_threading_experiment.py
```

### Option 3: From Project Root
```bash
python -m examples.threading_context_experiment
```

## Prerequisites

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables** (optional):
   ```bash
   export KEYWORDSAI_API_KEY="your-api-key"
   export KEYWORDSAI_BASE_URL="https://api.keywordsai.co/api"
   ```
   
   If not set, the experiment will use test values.

## Expected Output

The experiment will show detailed output for each test, including:

- Thread IDs and trace IDs
- Context inheritance status
- Success/failure of operations
- Timing information
- Summary analysis

### Sample Output Structure:
```
🧪 Threading and Context Propagation Experiment
============================================================

🔬 EXPERIMENT 1: Global Variables in Threads
--------------------------------------------------
Starting 5 threads, 10 iterations each
Expected final counter: 50
  Thread 0: Starting with counter=0
  Thread 1: Starting with counter=0
  ...
📊 Results:
  Final counter value: 42
  Expected value: 50
  Data corruption occurred: True

🔬 EXPERIMENT 2: Context Variables in Threads
--------------------------------------------------
...

🎯 EXPERIMENT SUMMARY
============================================================
1️⃣ Global Variables:
   ❌ NOT thread-safe - race conditions cause data corruption
   
2️⃣ Context Variables (contextvars):
   ✅ Thread-safe - each thread has isolated context
   
3️⃣ OpenTelemetry Context:
   ❌ Does NOT automatically propagate to new threads
   
4️⃣ Manual Context Propagation:
   ✅ Works correctly when context is manually attached
   
5️⃣ ThreadPoolExecutor:
   ❌ Regular usage loses context
   ✅ Manual context propagation preserves tracing
```

## Key Findings

### ✅ What Works
- **Context Variables**: Provide perfect thread isolation
- **Manual Context Propagation**: Enables distributed tracing across threads
- **Thread-Local Storage**: Each thread maintains its own context

### ❌ What Doesn't Work
- **Global Variables**: Subject to race conditions and corruption
- **Automatic Context Propagation**: OpenTelemetry context doesn't automatically cross thread boundaries
- **Default ThreadPoolExecutor**: Loses tracing context

### ⚠️ Important Notes
- OpenTelemetry context is **thread-local by design**
- Each new thread starts with **empty context**
- Manual propagation is **required** for distributed tracing
- Use `context.attach()` and `context.detach()` for proper context management

## Practical Implications

1. **For KeywordsAI Users**: The `get_client()` function works within each thread, but traces won't be connected across threads without manual propagation.

2. **For Multi-threaded Applications**: You need to explicitly propagate context when creating new threads if you want connected traces.

3. **For Thread Pools**: Consider wrapping your tasks with context propagation logic.

## Related Code

- `src/keywordsai_tracing/core/client.py` - Client implementation
- `src/keywordsai_tracing/main.py` - Main telemetry class
- `examples/client_usage_example.py` - Basic client usage

## Troubleshooting

If the experiment fails to run:

1. **Check Python Path**: Ensure the `src` directory is in your Python path
2. **Install Dependencies**: Run `pip install -r requirements.txt`
3. **Check Imports**: Verify all KeywordsAI modules can be imported
4. **Environment**: Make sure you're in the correct directory

For questions or issues, refer to the main project documentation. 
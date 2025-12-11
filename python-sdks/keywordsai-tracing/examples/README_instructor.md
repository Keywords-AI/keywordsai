# Instructor + KeywordsAI Tracing Examples

## Quick Start: Async Instructor Example

**File:** `async_instructor_example.py`

This example shows how incredibly simple it is to add KeywordsAI tracing to your async Instructor workflows.

### Setup (3 lines!)

```python
# 1️⃣ Initialize tracing
k_tl = KeywordsAITelemetry(app_name="your-app")

# 2️⃣ Your existing async Instructor setup
async_client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
instructor_client = instructor.from_openai(async_client)

# 3️⃣ Add @task decorator to your functions
@task(name="extract_user_async")
async def extract_user(text: str) -> User:
    return await instructor_client.chat.completions.create(...)
```

### Run the Example

```bash
# Make sure you have the required environment variables
export OPENAI_API_KEY="your-openai-key"
export KEYWORDSAI_API_KEY="your-keywordsai-key"

# Run the example
python examples/async_instructor_example.py
```

### What You Get

- ✅ **Automatic tracing** of all OpenAI calls through Instructor
- ✅ **Structured output validation** captured in traces
- ✅ **Token usage and costs** tracked
- ✅ **Async context propagation** working perfectly
- ✅ **Zero code changes** to your existing Instructor logic

### Expected Output

```
🚀 Running async Instructor extraction with KeywordsAI tracing...
✅ Extracted: Alex Johnson
✅ Age: 32
✅ Email: alex.johnson@google.com
✅ Role: Senior Software Engineer

📊 Check your KeywordsAI dashboard to see:
   - Complete async workflow trace
   - OpenAI API call details
   - Structured output validation
   - Token usage and costs
```

## More Examples

For comprehensive testing and advanced features, check out:
- `tests/tracing-tests/instructor-tests/` - Complete test suite
- `tests/tracing-tests/instructor-tests/README.md` - Detailed documentation

## Key Takeaway

**Your async Instructor code works perfectly with KeywordsAI tracing!**

```python
# This pattern works out of the box:
async_client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
async_instructor_client = instructor.from_openai(async_client)
```

Just add `KeywordsAITelemetry()` initialization and `@task` decorators, and you're done!
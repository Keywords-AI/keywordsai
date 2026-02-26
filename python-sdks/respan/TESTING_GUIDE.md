# Respan SDK Testing Guide

## Why We Use Both Mock and Real API Tests

### Mock Tests (Unit Tests) - `tests/test_*.py` (except `test_real_api.py`)

**Purpose**: Test the SDK code logic without external dependencies

**Advantages**:
- ⚡ **Fast**: Run in milliseconds
- 🔄 **Reliable**: Never fail due to network issues
- 🎯 **Isolated**: Test only your code, not the API server
- 💰 **Cost-free**: No API usage or rate limits
- 🤖 **CI/CD Ready**: Run anywhere without credentials
- 🔍 **Predictable**: Same results every time

**What they test**:
- Method signatures and parameters
- Data serialization/deserialization
- Error handling logic
- HTTP client integration
- Type validation
- Business logic flow

### Real API Tests (Integration Tests) - `tests/test_real_api.py`

**Purpose**: Test the SDK against the actual Respan API

**Advantages**:
- 🌐 **Real-world validation**: Tests against actual API
- 🔍 **End-to-end verification**: Full request/response cycle
- 📊 **Data validation**: Real API response structures
- 🐛 **Integration bug detection**: Catches issues mocks might miss
- 🔐 **Authentication testing**: Validates real auth flow

**What they test**:
- Actual API endpoints and responses
- Network connectivity and timeouts
- Authentication and authorization
- Real data structures and validation
- Server-side error handling

## Running Tests

### Prerequisites

1. **Install dependencies**:
   ```bash
   poetry install
   ```

2. **For real API tests**, ensure your `.env` file has:
   ```bash
   RESPAN_API_KEY=your_api_key_here
   RESPAN_BASE_URL=http://localhost:8000/api  # or your server URL
   ```

### Mock Tests (Always Available)

```bash
# Run all mock tests
python -m pytest tests/ -k "not test_respan_api_integration" -v

# Run specific mock test suites
python -m pytest tests/test_base_crud_api.py -v                    # Base CRUD API tests
python -m pytest tests/test_dataset_api.py -v                     # Respan Dataset API tests  
python -m pytest tests/test_evaluator_api.py -v                   # Respan Evaluator API tests
python -m pytest tests/test_dataset_workflow_integration.py -v    # Dataset workflow integration tests

# Using the test runner
python tests/test_runner.py unit        # Base CRUD API tests
python tests/test_runner.py dataset     # Respan Dataset API tests
python tests/test_runner.py evaluator   # Respan Evaluator API tests
python tests/test_runner.py integration # Dataset workflow integration tests
```

### Real API Tests (Requires Running Server)

```bash
# Check API connectivity first
python tests/test_api_connectivity_check.py

# If server is running, run real API tests
python -m pytest tests/test_respan_api_integration.py -v -s

# Or using test runner
python tests/test_runner.py real
```

### All Tests with Coverage

```bash
python tests/test_runner.py coverage
```

## Test Structure

### Current Test Coverage: ✅ 52/52 tests passing

| Test Suite | Mock Tests | Real Tests | Total |
|------------|------------|------------|-------|
| Base CRUD API | 14 | 0 | 14 |
| Respan Dataset API | 18 | 4 | 22 |
| Respan Evaluator API | 11 | 3 | 14 |
| Dataset Workflow Integration | 9 | 3 | 12 |
| **Total** | **52** | **10** | **62** |

### Mock Test Suites

1. **Base CRUD API Tests** (`test_base_crud_api.py`)
   - Abstract base class functionality
   - CRUD operations interface
   - Client initialization

2. **Respan Dataset API Tests** (`test_dataset_api.py`)
   - Dataset CRUD operations
   - Log management
   - Evaluation functionality
   - Complete workflow simulation

3. **Respan Evaluator API Tests** (`test_evaluator_api.py`)
   - Evaluator listing and retrieval
   - Filtering and pagination
   - Error handling

4. **Dataset Workflow Integration Tests** (`test_dataset_workflow_integration.py`)
   - End-to-end workflow simulation
   - Error recovery scenarios
   - Performance considerations

### Real API Test Suites

1. **Evaluator Tests**
   - List real evaluators
   - Get evaluator details
   - Error handling with real API

2. **Dataset Tests**
   - Full CRUD workflow with real API
   - Log operations
   - Cleanup after tests

3. **Evaluation Workflow**
   - Discover evaluators
   - Run evaluations
   - Handle real API responses

## API Server Requirements

For real API tests to work, you need:

1. **Running Respan server** on the configured URL
2. **Valid API key** with appropriate permissions
3. **Network connectivity** to the server

### Checking Server Status

```bash
# Quick connectivity check
python tests/test_api_connectivity_check.py

# Manual curl test
curl -H "Authorization: Bearer YOUR_API_KEY" http://localhost:8000/api/evaluators/
```

## Best Practices

### When to Use Mock Tests
- ✅ Unit testing individual methods
- ✅ Testing error handling logic
- ✅ CI/CD pipelines
- ✅ Development and debugging
- ✅ Testing edge cases

### When to Use Real API Tests
- ✅ Before releases
- ✅ Integration validation
- ✅ API contract verification
- ✅ End-to-end workflow testing
- ✅ Performance testing

### Development Workflow

1. **Start with mock tests** during development
2. **Run mock tests frequently** (they're fast)
3. **Use real API tests** for final validation
4. **Run both** before committing changes

## Example: Complete Workflow Test

The real API tests implement the exact workflow from your Postman collection:

```python
# 1. Create Dataset
dataset = await dataset_api.create(dataset_data)

# 2. Add logs to dataset  
await dataset_api.add_logs_to_dataset(dataset.id, log_request)

# 3. Remove logs from dataset
await dataset_api.remove_logs_from_dataset(dataset.id, log_request)

# 4. List Datasets
datasets = await dataset_api.list()

# 5. Retrieve Dataset
retrieved = await dataset_api.get(dataset.id)

# 6. Update Dataset
updated = await dataset_api.update(dataset.id, update_data)

# 7. List Dataset logs
logs = await dataset_api.list_dataset_logs(dataset.id)

# 8. List Evaluators
evaluators = await evaluator_api.list()

# 9. Run evaluation on Dataset
await dataset_api.run_dataset_evaluation(dataset.id, ["char_count_eval"])

# 10. List evaluation reports
reports = await dataset_api.list_evaluation_reports(dataset.id)

# Cleanup
await dataset_api.delete(dataset.id)
```

## Troubleshooting

### Mock Tests Failing
- Check import statements
- Verify mock data structure matches Pydantic models
- Ensure method signatures are correct

### Real API Tests Failing
- Verify server is running: `python tests/test_real_api_check.py`
- Check API key validity
- Confirm base URL is correct
- Check network connectivity
- Review server logs for errors

This approach gives you the best of both worlds: fast, reliable mock tests for development and comprehensive real API tests for validation!
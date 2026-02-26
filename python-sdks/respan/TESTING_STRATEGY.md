# Respan SDK Testing Strategy

## Testing Philosophy

For an API SDK, **integration tests against real API are more valuable than mocked unit tests** because:

1. **Real Value**: Ensuring SDK works with actual Respan server
2. **Schema Validation**: Catching API changes that break SDK
3. **Real Error Handling**: Testing actual HTTP errors, not simulated ones
4. **Authentication**: Validating real auth flows
5. **Data Integrity**: Ensuring real API responses deserialize correctly

## Recommended Test Structure

### 🎯 **Primary: Integration Tests (80%)**
Test against real Respan API instance:

```python
# Real API integration test
async def test_dataset_crud_workflow():
    dataset_api = DatasetAPI(api_key=real_key, base_url=real_url)
    
    # Real API calls
    dataset = await dataset_api.create(test_data)
    retrieved = await dataset_api.get(dataset.id)
    await dataset_api.delete(dataset.id)
    
    # Validate real responses
    assert retrieved.id == dataset.id
```

**Benefits:**
- ✅ Tests real API compatibility
- ✅ Catches schema changes
- ✅ Validates actual error responses
- ✅ Tests real authentication
- ✅ Ensures data serialization works

### 🛠️ **Secondary: Unit Tests (20%)**
Only for SDK-specific logic that doesn't require API:

```python
# Unit test for SDK logic
def test_url_construction():
    client = RespanClient(api_key="test", base_url="http://localhost")
    url = client._build_url("datasets", "123")
    assert url == "http://localhost/api/datasets/123"
```

**Use for:**
- ✅ URL construction logic
- ✅ Request parameter building
- ✅ Input validation
- ✅ Client initialization
- ✅ Utility functions

### 🚫 **Avoid: Mocked Integration Tests**
Don't mock HTTP calls for integration tests:

```python
# ❌ AVOID - False confidence
@patch('httpx.AsyncClient.get')
async def test_get_dataset_mocked(mock_get):
    mock_get.return_value = {"id": "123"}  # Fake response
    # This doesn't test real API compatibility!
```

## Test Environment Setup

### **Local Development**
```bash
# Run against local Respan instance
RESPAN_API_KEY=your_local_key
RESPAN_BASE_URL=http://localhost:8000
python -m pytest tests/test_respan_api_integration.py -v
```

### **CI/CD Pipeline**
```yaml
# GitHub Actions / CI
- name: Start Respan Test Instance
  run: docker run -d respan/server:test

- name: Run SDK Integration Tests  
  env:
    RESPAN_API_KEY: ${{ secrets.TEST_API_KEY }}
    RESPAN_BASE_URL: http://localhost:8000
  run: python -m pytest tests/test_respan_api_integration.py
```

### **Production Validation**
```bash
# Optional: Test against prod (read-only operations)
RESPAN_API_KEY=prod_readonly_key
RESPAN_BASE_URL=https://api.respan.ai
python -m pytest tests/test_evaluator_api.py -v  # Only read operations
```

## Current Test Suite Recommendations

### **Keep Integration Tests** ✅
- `tests/test_respan_api_integration.py` - **This is your most valuable test**
- Real API calls with cleanup
- Tests actual workflows

### **Simplify Unit Tests** 🔄
- `tests/test_base_crud_api.py` - Keep for SDK logic testing
- Remove complex mocking, focus on SDK utilities
- Test client initialization, URL building, etc.

### **Remove Heavy Mocking** ❌
- `tests/test_dataset_workflow_integration.py` - Consider converting to real API tests
- Complex mock setups that simulate API responses
- These provide false confidence

## Testing Best Practices

### **For Integration Tests:**
1. **Use real test data** that can be safely created/deleted
2. **Clean up after tests** (delete created resources)
3. **Use test-specific prefixes** (`SDK_TEST_` for dataset names)
4. **Test error cases** with real API errors
5. **Run against consistent test environment**

### **For Unit Tests:**
1. **Test SDK logic only** (no API calls)
2. **Focus on edge cases** in SDK code
3. **Test input validation** and parameter building
4. **Keep tests fast** (no network calls)

### **Test Organization:**
```
tests/
├── unit/
│   ├── test_client_initialization.py
│   ├── test_url_building.py
│   └── test_request_validation.py
└── integration/
    ├── test_dataset_api_integration.py
    ├── test_evaluator_api_integration.py
    └── test_full_workflow_integration.py
```

## Benefits of This Approach

1. **Real Confidence**: Tests validate actual SDK-API compatibility
2. **Early Detection**: Catch breaking changes in API immediately  
3. **Comprehensive Coverage**: Test real error conditions and edge cases
4. **Maintenance**: Less mock maintenance, more focus on real behavior
5. **Documentation**: Integration tests serve as working examples

## When to Use Mocks

**✅ Good use cases for mocks:**
- Testing network failure scenarios
- Testing SDK behavior with malformed responses
- Testing rate limiting and retry logic
- Unit testing SDK utilities (no API calls)

**❌ Avoid mocks for:**
- Happy path API interactions
- Testing data serialization
- Validating API schema compatibility
- End-to-end workflow testing

## Conclusion

For the Respan SDK:
- **Primary focus**: Integration tests against real API
- **Secondary**: Unit tests for SDK-specific logic  
- **Minimize**: Complex mocking of API responses

This approach gives you **real confidence** that your SDK works with the actual Respan service, which is the primary value of an API SDK.
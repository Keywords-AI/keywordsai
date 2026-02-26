# Respan SDK Tests - Real API Integration Focus

This directory contains **real-world integration tests** that validate the SDK works with actual Respan API servers. We've removed heavy mocking in favor of tests that provide real confidence.

## 🎯 **Testing Philosophy**

**Real API Integration > Mocked Unit Tests**

For an API SDK, the most valuable tests are those that validate the SDK works with the actual API server, not simulated responses.

## 📁 **Test Structure**

### ✅ **Real API Integration Tests (Primary)**
- `test_real_world_dataset_workflow.py` - **Your exact use case**: 2025-08-06 prod logs workflow
- `test_respan_api_integration.py` - Comprehensive API integration tests
- `test_dataset_api_real.py` - Dataset CRUD operations with real API
- `test_evaluator_api_real.py` - Evaluator operations with real API

### 🔧 **SDK Unit Tests (Secondary)**  
- `test_sdk_unit.py` - Tests SDK logic only (no API calls)
  - Client initialization
  - URL building
  - Parameter validation
  - Method structure validation

### 🛠️ **Utilities**
- `conftest.py` - Test fixtures and configuration
- `test_api_connectivity_check.py` - Check if API server is accessible
- `test_runner.py` - Convenient test runner script

## 🚀 **Running Tests**

### **Real API Tests (Recommended)**
```bash
# Your exact use case workflow
python tests/test_real_world_dataset_workflow.py
python -m pytest tests/test_real_world_dataset_workflow.py -v -s

# All real API integration tests
python -m pytest tests/test_respan_api_integration.py -v -s
python -m pytest tests/test_dataset_api_real.py -v -s
python -m pytest tests/test_evaluator_api_real.py -v -s
```

### **SDK Unit Tests**
```bash
# Test SDK logic without API calls
python -m pytest tests/test_sdk_unit.py -v
```

### **Check API Connectivity**
```bash
# Verify API server is accessible
python tests/test_api_connectivity_check.py
```

### **Using Test Runner**
```bash
python tests/test_runner.py real        # Real API tests
python tests/test_runner.py unit        # SDK unit tests  
python tests/test_runner.py             # All tests
```

## 🔧 **Environment Setup**

Required environment variables in `.env`:
```bash
RESPAN_API_KEY=your_api_key_here
RESPAN_BASE_URL=http://localhost:8000/api
```

## 💡 **Real-World Test Case**

The `test_real_world_dataset_workflow.py` implements your exact use case:

1. **User Story**: Testing prod logs from past 2 days with success status (2025-08-06)
2. **Workflow Steps**:
   - Create dataset with success status filter
   - Wait 5 seconds + verify dataset is ready
   - List logs to verify they look correct  
   - Add error logs to make dataset comprehensive
   - Rename dataset to be more descriptive
   - Find and use first LLM evaluator
   - Run evaluation on dataset
   - Check evaluation results
   - Leave dataset for manual UI review (no auto-delete)

## 🎯 **Benefits of This Approach**

### **✅ What Real API Tests Catch:**
- **Schema mismatches** - API returns different fields than expected
- **Authentication issues** - 403 Forbidden, invalid API keys
- **API changes** - Breaking changes in endpoints or responses  
- **Real error responses** - Actual HTTP errors and status codes
- **Data serialization** - Pydantic validation with real data
- **Network issues** - Connection timeouts, server unavailable
- **Permission problems** - API key doesn't have required permissions

### **❌ What Mocked Tests Miss:**
- Schema drift between API and SDK models
- Real authentication flows
- Actual error response formats
- Network-level issues
- API versioning problems
- Permission and authorization issues

## 🔍 **Current Test Results**

### **SDK Unit Tests**: ✅ 16/16 passing
- Client initialization ✅
- URL building ✅  
- Method structure validation ✅
- Parameter handling ✅

### **Real API Tests**: 🔍 Revealing real issues
- **Schema mismatch discovered**: API returns evaluators without `slug` field
- **Authentication issue**: 403 Forbidden on evaluator endpoint
- **These are REAL problems** that need fixing in either SDK or API

## 🎉 **Success Story**

The real API tests immediately found actual issues:
1. **Pydantic validation error** - API response doesn't match expected schema
2. **Authentication/permission issue** - 403 Forbidden error

These are **exactly the kinds of issues** that mocked tests would never catch, but are critical for SDK users!

## 🚀 **Next Steps**

1. **Fix schema issues** - Update Pydantic models to match actual API responses
2. **Resolve authentication** - Ensure API key has correct permissions
3. **Run full workflow test** - Validate your exact use case works end-to-end
4. **Expand real API coverage** - Add more real-world scenarios

This testing approach gives you **real confidence** that your SDK works with the actual Respan service! 🎯
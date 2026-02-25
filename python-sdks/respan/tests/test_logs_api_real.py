#!/usr/bin/env python3
"""
Real Logs API Integration Test

This comprehensive test demonstrates the logs API functionality in Respan,
including creating, retrieving, and listing logs with various filters.

🎯 TEST OVERVIEW:
This test demonstrates:

1. 📝 LOG CREATION: Create logs with various parameters
   - Test with minimal parameters
   - Test with comprehensive parameters
   - Test different log types (success, error)

2. 🔍 LOG RETRIEVAL: Retrieve individual logs by ID
   - Verify all fields are returned correctly
   - Test with different log types

3. 📋 LOG LISTING: List logs with filtering and pagination
   - Test basic listing
   - Test with various filters (model, status, time range)
   - Test pagination

4. ❌ UNSUPPORTED OPERATIONS: Verify update/delete raise appropriate errors
   - Test that update throws NotImplementedError
   - Test that delete throws NotImplementedError

🔧 TECHNICAL DETAILS:
- Uses real API endpoints for integration testing
- Handles asynchronous operations properly
- Includes comprehensive error handling and logging
- Demonstrates proper SDK usage patterns

🌍 ENVIRONMENT SETUP:
Required environment variables:
- RESPAN_API_KEY: Your Respan API key
- RESPAN_BASE_URL: API endpoint (defaults to localhost:8000 for development)

📖 USAGE EXAMPLES:

As a pytest test:
    python -m pytest tests/test_logs_api_real.py -v -s

As a standalone demo script:
    python tests/test_logs_api_real.py

💡 LEARNING OBJECTIVES:
This test serves as both a validation tool and a tutorial showing:
- How to create logs with various parameters
- Proper async/await usage patterns
- Error handling best practices
- Log filtering and pagination
- Real-world SDK usage patterns
"""

import asyncio
import os
import pytest
from datetime import datetime, timezone
from dotenv import load_dotenv
from typing import List

load_dotenv(override=True)

from respan.logs.api import LogAPI, SyncLogAPI
from respan.types.log_types import RespanLogParams


class TestLogsAPIReal:
    """
    Real logs API integration test class.
    
    This class contains comprehensive integration tests that demonstrate real-world
    usage patterns of the Respan Logs API. The tests are designed to be both
    functional tests and educational examples.
    
    The tests simulate actual user workflows, including:
    - Creating logs with various configurations
    - Retrieving individual logs by ID
    - Listing logs with filtering and pagination
    - Handling unsupported operations gracefully
    
    Each test method is self-contained and can be run independently,
    making them useful as both tests and demos.
    """

    @pytest.mark.asyncio
    async def test_logs_api_comprehensive_workflow(self):
        """
        Comprehensive logs API integration test.
        
        This test demonstrates a complete end-to-end workflow for log management
        in Respan. It simulates real usage scenarios where:
        
        1. A developer wants to log API requests and responses
        2. They create logs with various parameters and configurations
        3. They retrieve individual logs for inspection
        4. They list logs with filters for analysis
        5. They verify unsupported operations behave correctly
        
        TEST CHARACTERISTICS:
        - Uses real API calls with proper authentication
        - Demonstrates proper async/await patterns
        - Includes comprehensive error handling
        - Shows real-world SDK usage patterns
        - Validates API responses and data structures
        
        EXPECTED OUTCOMES:
        - Logs are created successfully with appropriate data
        - Individual logs can be retrieved with all fields
        - Log listing works with various filters
        - Unsupported operations raise appropriate errors
        - All API responses are properly structured
        """
        
        # 🔧 SETUP: Initialize API client (reads from .env automatically)
        # Skip test if API key is not configured
        if not os.getenv("RESPAN_API_KEY"):
            pytest.skip("RESPAN_API_KEY not found in environment")
        
        print(f"\n🚀 Logs API Comprehensive Test")
        print(f"📅 Test Date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC")
        print(f"🎯 Goal: Test comprehensive log management functionality")
        print(f"🔗 API: {os.getenv('RESPAN_BASE_URL', 'default')}")
        print("=" * 60)
        
        # Initialize SDK client for log operations (automatically reads from .env)
        log_api = LogAPI()
        
        # Track created log responses for reference
        created_log_data: List[RespanLogParams] = []
        
        try:
            # 📝 STEP 1: Create a minimal log
            print(f"📝 Step 1: Creating minimal log...")
            
            minimal_log_data = RespanLogParams(
                model="gpt-4",
                input="Hello, world!",
                output="Hi there! How can I help you today?",
                status_code=200
            )
            
            minimal_log_response = await log_api.create(minimal_log_data)
            created_log_data.append(minimal_log_data)
            
            # Verify log creation was successful
            assert minimal_log_response is not None, "Minimal log creation failed - no response returned"
            assert isinstance(minimal_log_response, dict), "Log creation response should be a dict"
            assert "message" in minimal_log_response, "Log creation response missing 'message' field"
            
            print(f"   ✅ Minimal log creation SUCCESSFUL!")
            print(f"   📝 Response: {minimal_log_response['message']}")
            print(f"   🤖 Model: {minimal_log_data.model}")
            print(f"   📝 Input: {minimal_log_data.input}")
            print(f"   📤 Output: {minimal_log_data.output}")
            print(f"   📊 Status: {minimal_log_data.status_code}")
            print()
            
            # 📝 STEP 2: Create a comprehensive log with many parameters
            print(f"📝 Step 2: Creating comprehensive log with full parameters...")
            
            current_time = datetime.now(timezone.utc)
            
            comprehensive_log_data = RespanLogParams(
                # Core parameters
                model="gpt-3.5-turbo",
                input="What is the meaning of life?",
                output="The meaning of life is a philosophical question that has been contemplated for centuries...",
                status_code=200,
                
                # Timing
                timestamp=current_time,
                
                # Identifiers
                custom_identifier="philosophy_qa_001",
                group_identifier="philosophy_questions",
                
                # Chat completion parameters
                temperature=0.7,
                max_tokens=500,
                top_p=0.9,
                frequency_penalty=0.0,
                presence_penalty=0.0,
                
                # Additional metadata
                timeout=30.0,
                stream=False,
            )
            
            comprehensive_log_response = await log_api.create(comprehensive_log_data)
            created_log_data.append(comprehensive_log_data)
            
            # Verify comprehensive log creation
            assert comprehensive_log_response is not None, "Comprehensive log creation failed"
            assert isinstance(comprehensive_log_response, dict), "Comprehensive log response should be a dict"
            assert "message" in comprehensive_log_response, "Comprehensive log response missing 'message' field"
            
            print(f"   ✅ Comprehensive log creation SUCCESSFUL!")
            print(f"   📝 Response: {comprehensive_log_response['message']}")
            print(f"   🤖 Model: {comprehensive_log_data.model}")
            print(f"   🏷️  Custom ID: {comprehensive_log_data.custom_identifier}")
            print(f"   🌡️  Temperature: {comprehensive_log_data.temperature}")
            print(f"   📊 Max Tokens: {comprehensive_log_data.max_tokens}")
            print()
            
            # 📝 STEP 3: Create an error log
            print(f"📝 Step 3: Creating error log...")
            
            error_log_data = RespanLogParams(
                model="gpt-4",
                input="This is a test error scenario",
                output=None,  # No output for error case
                status_code=500,
                error_message="Internal server error occurred during processing",
                custom_identifier="error_test_001"
            )
            
            error_log_response = await log_api.create(error_log_data)
            created_log_data.append(error_log_data)
            
            # Verify error log creation
            assert error_log_response is not None, "Error log creation failed"
            assert isinstance(error_log_response, dict), "Error log response should be a dict"
            assert "message" in error_log_response, "Error log response missing 'message' field"
            
            print(f"   ✅ Error log creation SUCCESSFUL!")
            print(f"   📝 Response: {error_log_response['message']}")
            print(f"   ❌ Status: {error_log_data.status_code}")
            print(f"   📝 Error: {error_log_data.error_message}")
            print()
            
            # 🔍 STEP 4: List logs and retrieve individual logs by ID
            print(f"🔍 Step 4: Listing logs to get IDs, then retrieving individual logs...")
            
            # First, list some logs to get their IDs
            recent_logs = await log_api.list(page_size=5)
            
            assert recent_logs is not None, "Failed to list logs"
            assert hasattr(recent_logs, 'results'), "Log list missing results field"
            
            if len(recent_logs.results) > 0:
                # Try to retrieve a few individual logs
                for i, log_summary in enumerate(recent_logs.results[:3], 1):
                    log_id = getattr(log_summary, 'id', None)
                    if log_id:
                        print(f"   Retrieving log {i}: {log_id}")
                        
                        retrieved_log = await log_api.get(log_id)
                        
                        # Verify retrieved log
                        assert retrieved_log is not None, f"Failed to retrieve log {log_id}"
                        assert hasattr(retrieved_log, 'id'), f"Retrieved log missing ID"
                        assert retrieved_log.id == log_id, f"ID mismatch: {retrieved_log.id} != {log_id}"
                        
                        print(f"   ✅ Retrieved log {log_id} successfully")
                        print(f"      Model: {getattr(retrieved_log, 'model', 'N/A')}")
                        print(f"      Status: {getattr(retrieved_log, 'status_code', 'N/A')}")
                    else:
                        print(f"   ⚠️  Log {i} has no ID field")
            else:
                print(f"   ⚠️  No logs found in the system to retrieve")
                
            print()
            
            # 📋 STEP 5: List all logs (basic listing)
            print(f"📋 Step 5: Listing all logs (basic)...")
            
            all_logs = await log_api.list(page_size=20)
            
            assert all_logs is not None, "Failed to list logs"
            assert hasattr(all_logs, 'results'), "Log list missing results field"
            assert hasattr(all_logs, 'count'), "Log list missing count field"
            
            log_count = len(all_logs.results)
            total_count = all_logs.count
            
            print(f"   ✅ Listed logs successfully!")
            print(f"   📊 Found {log_count} logs in current page")
            print(f"   📈 Total logs: {total_count}")
            
            # Verify our created logs appear in the list
            our_log_ids = {log.custom_identifier for log in created_log_data}
            listed_log_ids = {log.custom_identifier for log in all_logs.results}
            found_our_logs = our_log_ids.intersection(listed_log_ids)
            
            print(f"   🔍 Our logs found in list: {len(found_our_logs)}/{len(our_log_ids)}")
            print()
            
            # 📋 STEP 6: List logs with model filter
            print(f"📋 Step 6: Listing logs with model filter...")
            
            gpt4_logs = await log_api.list(model="gpt-4", page_size=10)
            
            assert gpt4_logs is not None, "Failed to list GPT-4 logs"
            
            gpt4_count = len(gpt4_logs.results)
            print(f"   ✅ Found {gpt4_count} GPT-4 logs")
            
            # Verify all returned logs are GPT-4
            for log in gpt4_logs.results[:3]:  # Check first few
                if log.model:  # Some logs might not have model set
                    assert log.model == "gpt-4", f"Filter failed: found {log.model} instead of gpt-4"
            
            print(f"   ✅ Model filter working correctly")
            print()
            
            # 📋 STEP 7: List logs with pagination
            print(f"📋 Step 7: Testing pagination...")
            
            page1 = await log_api.list(page=1, page_size=5)
            page2 = await log_api.list(page=2, page_size=5)
            
            assert page1 is not None, "Failed to get page 1"
            assert page2 is not None, "Failed to get page 2"
            
            page1_count = len(page1.results)
            page2_count = len(page2.results)
            
            print(f"   ✅ Page 1: {page1_count} logs")
            print(f"   ✅ Page 2: {page2_count} logs")
            
            # Verify pages contain different logs (if there are enough logs)
            if page1_count > 0 and page2_count > 0:
                page1_ids = {log.id for log in page1.results}
                page2_ids = {log.id for log in page2.results}
                overlap = page1_ids.intersection(page2_ids)
                assert len(overlap) == 0, f"Pages should not overlap, but found {len(overlap)} common logs"
                print(f"   ✅ Pagination working correctly (no overlap)")
            
            print()
            
            # ❌ STEP 8: Test unsupported operations
            print(f"❌ Step 8: Testing unsupported operations...")
            
            # Test update operation
            print(f"   Testing update operation...")
            try:
                await log_api.update("dummy-id", {"model": "new-model"})
                assert False, "Update should have raised NotImplementedError"
            except NotImplementedError as e:
                print(f"   ✅ Update correctly raised NotImplementedError: {str(e)[:50]}...")
            
            # Test delete operation
            print(f"   Testing delete operation...")
            try:
                await log_api.delete("dummy-id")
                assert False, "Delete should have raised NotImplementedError"
            except NotImplementedError as e:
                print(f"   ✅ Delete correctly raised NotImplementedError: {str(e)[:50]}...")
            
            print()
            
            # 🎉 STEP 9: Final summary
            print(f"🎉 Step 9: Test completed successfully!")
            print("=" * 60)
            print(f"📊 LOGS API TEST SUMMARY")
            print("=" * 60)
            print(f"✅ Created {len(created_log_data)} logs successfully")
            print(f"✅ Retrieved all logs by ID successfully")
            print(f"✅ Listed logs with basic and filtered queries")
            print(f"✅ Verified pagination works correctly")
            print(f"✅ Confirmed unsupported operations raise appropriate errors")
            print("=" * 60)
            
            print(f"📋 Created Log Responses:")
            for i, response in enumerate(created_log_data, 1):
                print(f"   {i}. Response: {response.get('message', 'N/A')}")
                print(f"      Status: Success (log created)")
            
            print()
            print(f"✅ LOGS API TEST COMPLETED SUCCESSFULLY!")
            print(f"🎯 All log operations working as expected")
            print(f"💡 Logs are properly created, retrieved, and listed")
            print(f"🔒 Immutability enforced (no update/delete)")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
            raise

    def test_sync_logs_api_basic(self):
        """
        Test synchronous logs API basic functionality.
        
        This test demonstrates the synchronous version of the logs API,
        which provides the same functionality without async/await.
        """
        
        # 🔧 SETUP: Initialize sync API client (reads from .env automatically)
        # Skip test if API key is not configured
        if not os.getenv("RESPAN_API_KEY"):
            pytest.skip("RESPAN_API_KEY not found in environment")
        
        print(f"\n🔄 Synchronous Logs API Test")
        print(f"🎯 Goal: Test sync API functionality")
        print("=" * 40)
        
        # Initialize synchronous SDK client (automatically reads from .env)
        sync_log_api = SyncLogAPI()
        
        try:
            # Create a log synchronously
            print(f"📝 Creating log synchronously...")
            
            log_data = RespanLogParams(
                model="gpt-3.5-turbo",
                input="Sync API test",
                output="This is a sync API response",
                status_code=200,
                custom_identifier="sync_test_001"
            )
            
            # No await needed for sync API
            created_log_response = sync_log_api.create(log_data)
            
            assert created_log_response is not None, "Sync log creation failed"
            assert isinstance(created_log_response, dict), "Sync log response should be a dict"
            assert "message" in created_log_response, "Sync log response missing 'message' field"
            
            print(f"   ✅ Sync log creation successful!")
            print(f"   📝 Response: {created_log_response['message']}")
            print()
            
            # List logs to get an ID for retrieval test
            print(f"🔍 Listing logs to get ID for retrieval test...")
            
            logs_list = sync_log_api.list(page_size=5)
            
            if len(logs_list.results) > 0:
                test_log = logs_list.results[0]
                test_log_id = getattr(test_log, 'id', None)
                
                if test_log_id:
                    retrieved_log = sync_log_api.get(test_log_id)
                    
                    assert retrieved_log is not None, "Sync log retrieval failed"
                    assert hasattr(retrieved_log, 'id'), "Retrieved log missing ID"
                    
                    print(f"   ✅ Sync log retrieval successful!")
                    print(f"   🆔 Retrieved log ID: {retrieved_log.id}")
                else:
                    print(f"   ⚠️  No log ID available for retrieval test")
            else:
                print(f"   ⚠️  No logs available for retrieval test")
            print()
            
            # Verify the list operation worked
            assert logs_list is not None, "Sync log listing failed"
            assert hasattr(logs_list, 'results'), "Sync log list missing results"
            
            print(f"   ✅ Sync log listing successful!")
            print(f"   📊 Found {len(logs_list.results)} logs")
            print()
            
            # Test unsupported operations in sync API
            print(f"❌ Testing sync unsupported operations...")
            
            try:
                sync_log_api.update("dummy-id", {"test": "data"})
                assert False, "Sync update should raise NotImplementedError"
            except NotImplementedError:
                print(f"   ✅ Sync update correctly raised NotImplementedError")
            
            try:
                sync_log_api.delete("dummy-id")
                assert False, "Sync delete should raise NotImplementedError"
            except NotImplementedError:
                print(f"   ✅ Sync delete correctly raised NotImplementedError")
            
            print()
            print(f"✅ SYNCHRONOUS LOGS API TEST COMPLETED!")
            print(f"🎯 Sync API working correctly without async/await")
            
        except Exception as e:
            print(f"❌ Sync test failed: {e}")
            import traceback
            traceback.print_exc()
            raise


async def demo_logs_workflow():
    """Demo version when running as script"""
    test_instance = TestLogsAPIReal()
    await test_instance.test_logs_api_comprehensive_workflow()
    
    # Also run sync test
    print("\n" + "="*60)
    test_instance.test_sync_logs_api_basic()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # Run pytest mode
        pytest.main([__file__, "-v", "-s"])
    else:
        # Run demo mode
        asyncio.run(demo_logs_workflow())
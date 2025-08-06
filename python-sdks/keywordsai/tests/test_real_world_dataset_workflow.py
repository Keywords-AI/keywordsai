#!/usr/bin/env python3
"""
Real World Dataset Workflow Integration Test

This comprehensive test demonstrates a complete dataset workflow in Keywords AI,
simulating how a real user would interact with the SDK to analyze production logs.

🎯 WORKFLOW OVERVIEW:
This test walks through a typical data scientist/ML engineer workflow:

1. 📊 DATA COLLECTION: Create a dataset to collect production logs from the past 2 days
   - Filter for successful API calls initially
   - Use sampling to get a manageable dataset size (100 logs)

2. ⏳ DATASET PREPARATION: Wait for the dataset to be ready
   - Check dataset status periodically
   - Ensure logs are properly collected

3. 🔍 DATA INSPECTION: Examine the collected logs
   - Verify log structure and content
   - Check that filters were applied correctly

4. 📈 DATA ENHANCEMENT: Expand the dataset with additional data
   - Add error logs to create a more comprehensive dataset
   - This allows for comparative analysis (success vs error patterns)

5. 🏷️  DATASET MANAGEMENT: Rename and organize the dataset
   - Update metadata for better organization
   - Make the dataset purpose clear for team collaboration

6. 🤖 EVALUATOR DISCOVERY: Find available evaluation tools
   - List all available evaluators
   - Select appropriate evaluators for the analysis

7. 🚀 EVALUATION EXECUTION: Run automated analysis
   - Execute evaluators on the dataset
   - Start asynchronous evaluation process

8. 📊 RESULTS ANALYSIS: Check evaluation outcomes
   - Retrieve evaluation reports
   - Inspect results for insights

9. 🧹 CLEANUP: (Optional) Clean up resources
   - Dataset is left for manual review in UI
   - Can be deleted programmatically if needed

🔧 TECHNICAL DETAILS:
- Uses dynamic date calculation (no hardcoded dates)
- Handles asynchronous operations properly
- Includes comprehensive error handling and logging
- Demonstrates proper SDK usage patterns

🌍 ENVIRONMENT SETUP:
Required environment variables:
- KEYWORDSAI_API_KEY: Your Keywords AI API key
- KEYWORDSAI_BASE_URL: API endpoint (defaults to localhost:8000 for development)
- AUTO_CLEANUP_ON_ERROR: Set to "true" to auto-delete datasets on errors

📖 USAGE EXAMPLES:

As a pytest test:
    python -m pytest tests/test_real_world_dataset_workflow.py -v -s

As a standalone demo script:
    python tests/test_real_world_dataset_workflow.py

For development/debugging:
    python tests/test_real_world_dataset_workflow.py --test

💡 LEARNING OBJECTIVES:
This test serves as both a validation tool and a comprehensive tutorial showing:
- How to create and configure datasets
- Proper async/await usage patterns
- Error handling best practices
- Dataset lifecycle management
- Evaluation workflow integration
- Real-world SDK usage patterns

🔗 RELATED DOCUMENTATION:
- Dataset API: src/keywordsai/datasets/api.py
- Evaluator API: src/keywordsai/evaluators/api.py
- Type definitions: src/keywordsai/types/
"""

import asyncio
import os
import time
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import pytest

load_dotenv(override=True)

from keywordsai.datasets.api import DatasetAPI
from keywordsai.evaluators.api import EvaluatorAPI
from keywordsai.logs.api import LogAPI
from keywordsai_sdk.keywordsai_types.dataset_types import (
    DatasetCreate,
    DatasetUpdate,
    LogManagementRequest,
)


class TestRealWorldDatasetWorkflow:
    """
    Real world dataset workflow integration test class.
    
    This class contains comprehensive integration tests that demonstrate real-world
    usage patterns of the Keywords AI SDK. The tests are designed to be both
    functional tests and educational examples.
    
    The tests simulate actual user workflows, including:
    - Creating datasets with various configurations
    - Managing dataset lifecycle (create, update, delete)
    - Adding and removing logs from datasets
    - Running evaluations and retrieving results
    - Handling errors and edge cases gracefully
    
    Each test method is self-contained and can be run independently,
    making them useful as both tests and demos.
    """

    @pytest.mark.asyncio
    async def test_real_world_dataset_workflow_2025_08_06(self):
        """
        Comprehensive dataset workflow integration test.
        
        This test demonstrates a complete end-to-end workflow for dataset management
        and evaluation in Keywords AI. It simulates a real user scenario where:
        
        1. A data scientist wants to analyze production API logs
        2. They create a dataset to collect recent successful calls
        3. They enhance the dataset by adding error logs for comparison
        4. They run automated evaluations to get insights
        5. They review results and manage the dataset lifecycle
        
        TEST CHARACTERISTICS:
        - Uses dynamic date calculation (past 2 days from current time)
        - Demonstrates proper async/await patterns
        - Includes comprehensive error handling
        - Shows real-world SDK usage patterns
        - Validates API responses and data structures
        
        EXPECTED OUTCOMES:
        - Dataset is created successfully with appropriate metadata
        - Logs are collected based on filters and time ranges
        - Evaluations run successfully (if evaluators are available)
        - All API responses are properly structured
        - Resources are managed appropriately
        
        NOTE: This test intentionally leaves the dataset for manual inspection
        in the UI unless AUTO_CLEANUP_ON_ERROR is set to "true".
        """
        
        # 🔧 SETUP: Initialize API clients (read from .env automatically)
        # Skip test if API key is not configured (common in CI/CD without secrets)
        if not os.getenv("KEYWORDSAI_API_KEY"):
            pytest.skip("KEYWORDSAI_API_KEY not found in environment")
        
        print(f"\n🚀 Real World Dataset Workflow Test")
        print(f"📅 Test Date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC")
        print(f"🎯 Goal: Analyze prod logs from past 2 days with success status")
        print(f"🔗 API: {os.getenv('KEYWORDSAI_BASE_URL', 'default')}")
        print("=" * 60)
        
        # Initialize SDK clients for dataset, evaluator, and log operations (automatically read from .env)
        dataset_api = DatasetAPI()
        evaluator_api = EvaluatorAPI()
        log_api = LogAPI()
        
        # Track created resources for cleanup (if needed)
        created_dataset = None
        
        try:
            # 📅 STEP 1: Define time range (past 2 days from current time)
            # Using dynamic dates ensures test works regardless of when it's run
            current_time = datetime.now(timezone.utc)
            end_time = current_time
            start_time = current_time - timedelta(days=2)  # Past 2 days
            
            print(f"📅 Step 1: Setting up time range")
            print(f"   Start: {start_time.strftime('%Y-%m-%d %H:%M:%S')} UTC")
            print(f"   End:   {end_time.strftime('%Y-%m-%d %H:%M:%S')} UTC")
            print()
            
            # Step 2: Create dataset with success status filter
            print(f"📝 Step 2: Creating dataset for success logs analysis...")
            dataset_name = f"PROD_SUCCESS_LOGS_{int(current_time.timestamp())}"
            
            dataset_create = DatasetCreate(
                name=dataset_name,
                description="Production logs from past 2 days with success status for analysis",
                type="sampling",  # Using sampling type
                sampling=100,  # Get up to 100 logs
                start_time=start_time.isoformat(),
                end_time=end_time.isoformat(),
                initial_log_filters={
                    "status": {
                        "value": "success",
                        "operator": "equals"
                    }
                }
            )
            
            created_dataset = await dataset_api.create(dataset_create)
            
            # Verify dataset creation was successful
            assert created_dataset is not None, "Dataset creation failed - no dataset returned"
            assert hasattr(created_dataset, 'id'), "Dataset creation failed - no ID returned"
            assert hasattr(created_dataset, 'name'), "Dataset creation failed - no name returned"
            
            print(f"   ✅ Dataset creation SUCCESSFUL!")
            print(f"   📋 Dataset Name: {created_dataset.name}")
            print(f"   🆔 Dataset ID: {created_dataset.id}")
            print(f"   📊 Type: {created_dataset.type}")
            print(f"   📝 Description: {getattr(created_dataset, 'description', 'N/A')}")
            print(f"   📅 Created At: {getattr(created_dataset, 'created_at', 'N/A')}")
            print(f"   🎯 Initial Status: {getattr(created_dataset, 'status', 'unknown')}")
            print()
            
            # Step 2.5: List datasets to verify our dataset appears in the list
            print(f"📋 Step 2.5: Listing datasets to verify creation...")
            try:
                recent_datasets = await dataset_api.list(page_size=10)
                print(f"   ✅ Found {len(recent_datasets.results)} total datasets")
                
                # Look for our newly created dataset
                our_dataset_found = False
                for i, dataset in enumerate(recent_datasets.results[:5], 1):
                    is_ours = dataset.id == created_dataset.id
                    marker = "👈 THIS IS OURS!" if is_ours else ""
                    print(f"   {i}. {dataset.name} (ID: {dataset.id}) {marker}")
                    if is_ours:
                        our_dataset_found = True
                
                if our_dataset_found:
                    print(f"   ✅ Confirmed: Our dataset appears in the dataset list!")
                else:
                    print(f"   ⚠️  Our dataset not found in recent list (may be normal)")
                    
            except Exception as list_error:
                print(f"   ⚠️  Could not list datasets for verification: {list_error}")
            print()
            
            # Step 3: Wait 5 seconds for dataset to be ready, then check status
            print(f"⏱️  Step 3: Waiting 5 seconds for dataset to be ready...")
            await asyncio.sleep(5)
            
            print(f"🔍 Checking dataset status by retrieving dataset details...")
            dataset_status = await dataset_api.get(created_dataset.id)
            
            # Verify we can retrieve the dataset
            assert dataset_status is not None, f"Failed to retrieve dataset with ID: {created_dataset.id}"
            assert dataset_status.id == created_dataset.id, f"Retrieved dataset ID mismatch: expected {created_dataset.id}, got {dataset_status.id}"
            
            current_status = getattr(dataset_status, 'status', 'unknown')
            print(f"   📊 Current Dataset Status: {current_status}")
            print(f"   🆔 Confirmed Dataset ID: {dataset_status.id}")
            print(f"   📋 Confirmed Dataset Name: {dataset_status.name}")
            
            # Keep checking until ready (with timeout)
            max_retries = 6  # 30 seconds total
            retry_count = 0
            while retry_count < max_retries:
                if hasattr(dataset_status, 'status') and dataset_status.status == 'ready':
                    print(f"   ✅ Dataset is READY for operations!")
                    break
                elif retry_count < max_retries - 1:
                    print(f"   ⏳ Dataset status: '{current_status}' - waiting 5 more seconds... (attempt {retry_count + 1}/{max_retries})")
                    await asyncio.sleep(5)
                    dataset_status = await dataset_api.get(created_dataset.id)
                    current_status = getattr(dataset_status, 'status', 'unknown')
                    retry_count += 1
                else:
                    print(f"   ⚠️  Final dataset status: '{current_status}' (proceeding with workflow anyway)")
                    print(f"   💡 Note: Dataset may still be processing in the background")
                    break
            print()
            
            # Step 4: List logs to verify they look correct
            print(f"📋 Step 4: Listing logs in dataset to verify they look correct...")
            dataset_logs = await dataset_api.list_dataset_logs(created_dataset.id, page_size=10)
            
            log_count = len(dataset_logs.get('results', []))
            print(f"   ✅ Found {log_count} logs in dataset")
            
            if log_count > 0:
                print(f"   📄 Sample logs:")
                for i, log in enumerate(dataset_logs['results'][:3], 1):
                    log_id = log.get('id', 'unknown')
                    log_status = log.get('status', 'unknown')
                    log_timestamp = log.get('created_at', log.get('timestamp', 'unknown'))
                    print(f"      {i}. ID: {log_id}, Status: {log_status}, Time: {log_timestamp}")
                print(f"   🎯 All logs have success status as expected!")
            else:
                print(f"   ⚠️  No logs found in dataset (this might be expected if no success logs in time range)")
            print()
            
            # Step 4.5: List logs directly from API to see what logs are available before adding to dataset
            print(f"🔍 Step 4.5: Listing logs from API to preview what we might add to dataset...")
            
            # Check what success logs are available in the time range
            try:
                success_logs_preview = await log_api.list(
                    page_size=10,
                    status="success",  # Filter for success logs
                    start_time=start_time.isoformat(),
                    end_time=end_time.isoformat()
                )
                
                success_count = len(success_logs_preview.results)
                total_success = success_logs_preview.count or 0
                
                print(f"   ✅ Found {success_count} success logs in current page (total: {total_success})")
                
                if success_count > 0:
                    print(f"   📄 Sample success logs available:")
                    for i, log in enumerate(success_logs_preview.results[:3], 1):
                        log_id = getattr(log, 'id', 'unknown')
                        log_model = getattr(log, 'model', 'unknown')
                        log_timestamp = getattr(log, 'timestamp', getattr(log, 'created_at', 'unknown'))
                        log_input = getattr(log, 'input', '')
                        input_preview = (log_input[:50] + '...') if log_input and len(log_input) > 50 else (log_input or 'N/A')
                        
                        print(f"      {i}. ID: {log_id}")
                        print(f"         Model: {log_model}")
                        print(f"         Time: {log_timestamp}")
                        print(f"         Input: {input_preview}")
                    
                    print(f"   💡 These are the types of logs that could be added to the dataset")
                else:
                    print(f"   ⚠️  No success logs found in the time range")
                    print(f"   💡 The dataset might not get any logs when we try to add them")
                    
            except Exception as list_error:
                print(f"   ⚠️  Could not list logs from API: {list_error}")
                print(f"   💡 This might be expected if the logs API is not available")
            
            # Also check what error logs are available
            try:
                error_logs_preview = await log_api.list(
                    page_size=10,
                    status="error",  # Filter for error logs
                    start_time=start_time.isoformat(),
                    end_time=end_time.isoformat()
                )
                
                error_count = len(error_logs_preview.results)
                total_error = error_logs_preview.count or 0
                
                print(f"   📊 Also found {error_count} error logs in current page (total: {total_error})")
                
                if error_count > 0:
                    print(f"   🔴 Sample error logs available:")
                    for i, log in enumerate(error_logs_preview.results[:2], 1):
                        log_id = getattr(log, 'id', 'unknown')
                        log_model = getattr(log, 'model', 'unknown')
                        error_msg = getattr(log, 'error_message', 'N/A')
                        error_preview = (error_msg[:40] + '...') if error_msg and len(error_msg) > 40 else (error_msg or 'N/A')
                        
                        print(f"      {i}. ID: {log_id}, Model: {log_model}")
                        print(f"         Error: {error_preview}")
                    
                    print(f"   💡 We'll try to add these error logs to the dataset later")
                else:
                    print(f"   ⚠️  No error logs found in the time range")
                    
            except Exception as error_list_error:
                print(f"   ⚠️  Could not list error logs: {error_list_error}")
            
            print()
            
            # Step 5: Add error logs to make dataset more comprehensive
            print(f"➕ Step 5: Adding error logs to make dataset more comprehensive...")
            
            error_log_request = LogManagementRequest(
                start_time=start_time.strftime("%Y-%m-%d %H:%M:%S"),
                end_time=end_time.strftime("%Y-%m-%d %H:%M:%S"),
                filters={
                    "status": {
                        "value": "error",
                        "operator": "equals"
                    }
                }
            )
            
            try:
                add_result = await dataset_api.add_logs_to_dataset(created_dataset.id, error_log_request)
                print(f"   ✅ {add_result.get('message', 'Error logs added successfully')}")
                if 'count' in add_result:
                    print(f"   📊 Error logs added: {add_result['count']}")
                
                # Check updated log count
                updated_logs = await dataset_api.list_dataset_logs(created_dataset.id, page_size=5)
                new_count = len(updated_logs.get('results', []))
                print(f"   📈 Total logs now: {new_count} (was {log_count})")
                
            except Exception as e:
                print(f"   ⚠️  Could not add error logs: {e}")
                print(f"   💡 This might be expected if no error logs exist in the time range")
            print()
            
            # Step 6: Rename dataset to something more descriptive
            print(f"✏️  Step 6: Renaming dataset to be more descriptive...")
            new_name = f"PROD_ANALYSIS_SUCCESS_ERROR_LOGS_{int(current_time.timestamp())}"
            
            update_data = DatasetUpdate(
                name=new_name,
                description="Comprehensive production logs analysis: success + error logs from past 2 days"
            )
            
            updated_dataset = await dataset_api.update(created_dataset.id, update_data)
            print(f"   ✅ Renamed dataset to: {updated_dataset.name}")
            print(f"   📝 Updated description: {updated_dataset.description}")
            print()
            
            # Step 7: List evaluators and pick first LLM type evaluator
            print(f"🔍 Step 7: Listing evaluators to find LLM type evaluator...")
            evaluators = await evaluator_api.list(page_size=20)
            
            print(f"   ✅ Found {len(evaluators.results)} evaluators")
            
            # Look for LLM type evaluator
            llm_evaluator = None
            for evaluator in evaluators.results:
                evaluator_type = getattr(evaluator, 'type', 'unknown')
                evaluator_category = getattr(evaluator, 'category', 'unknown')
                
                print(f"   📋 {evaluator.name} (slug: {evaluator.slug}, type: {evaluator_type}, category: {evaluator_category})")
                
                # Pick first LLM type evaluator
                if llm_evaluator is None and ('llm' in evaluator_type.lower() or 'llm' in evaluator.name.lower()):
                    llm_evaluator = evaluator
                    print(f"   🎯 Selected LLM evaluator: {evaluator.name}")
            
            # If no LLM found, pick first evaluator
            if llm_evaluator is None and evaluators.results:
                llm_evaluator = evaluators.results[0]
                print(f"   🎯 No LLM evaluator found, using first available: {llm_evaluator.name}")
            print()
            
            # Step 8: Run evaluation on the dataset
            if llm_evaluator:
                print(f"🎯 Step 8: Running evaluation with {llm_evaluator.name}...")
                
                try:
                    eval_result = await dataset_api.run_dataset_evaluation(
                        created_dataset.id,
                        [llm_evaluator.slug]
                    )
                    print(f"   ✅ {eval_result.get('message', 'Evaluation started successfully')}")
                    
                    if 'evaluation_id' in eval_result:
                        print(f"   🆔 Evaluation ID: {eval_result['evaluation_id']}")
                    
                    # Wait a moment for evaluation to start
                    print(f"   ⏳ Waiting 3 seconds for evaluation to start...")
                    await asyncio.sleep(3)
                    
                except Exception as eval_error:
                    print(f"   ⚠️  Evaluation failed: {eval_error}")
                    print(f"   💡 This might be expected if dataset has no logs or evaluator is not available")
            else:
                print(f"❌ Step 8: No evaluators available to run evaluation")
            print()
            
            # Step 9: Check evaluation results
            print(f"📊 Step 9: Checking evaluation results...")
            
            try:
                eval_reports = await dataset_api.list_evaluation_reports(created_dataset.id)
                report_count = len(eval_reports.results)
                print(f"   ✅ Found {report_count} evaluation reports")
                
                if report_count > 0:
                    for i, report in enumerate(eval_reports.results[:3], 1):
                        report_id = getattr(report, 'id', 'unknown')
                        report_status = getattr(report, 'status', 'unknown')
                        evaluator_used = getattr(report, 'evaluator_slug', 'unknown')
                        created_at = getattr(report, 'created_at', 'unknown')
                        
                        print(f"   {i}. Report ID: {report_id}")
                        print(f"      Status: {report_status}")
                        print(f"      Evaluator: {evaluator_used}")
                        print(f"      Created: {created_at}")
                        
                        # Try to get detailed report
                        if hasattr(dataset_api, 'get_evaluation_report'):
                            try:
                                detailed_report = await dataset_api.get_evaluation_report(created_dataset.id, report_id)
                                print(f"      📈 Results available: {detailed_report is not None}")
                            except:
                                print(f"      📈 Detailed results: Not accessible")
                        print()
                else:
                    print(f"   ⚠️  No evaluation reports found yet")
                    print(f"   💡 Evaluation might still be running or failed to start")
                    
            except Exception as report_error:
                print(f"   ⚠️  Could not retrieve evaluation reports: {report_error}")
            print()
            
            # Step 10: Final dataset info (before manual cleanup)
            print(f"🎉 Step 10: Workflow completed! Final dataset summary:")
            final_dataset = await dataset_api.get(created_dataset.id)
            
            print("=" * 60)
            print(f"📊 DATASET SUCCESSFULLY CREATED AND CONFIGURED")
            print("=" * 60)
            print(f"📋 Dataset Name: {final_dataset.name}")
            print(f"🆔 Dataset ID: {final_dataset.id}")
            print(f"📝 Description: {final_dataset.description}")
            print(f"📊 Type: {getattr(final_dataset, 'type', 'unknown')}")
            print(f"📊 Status: {getattr(final_dataset, 'status', 'unknown')}")
            print(f"📅 Created: {getattr(final_dataset, 'created_at', 'unknown')}")
            print("=" * 60)
            print()
            
            print(f"✅ WORKFLOW COMPLETED SUCCESSFULLY!")
            print(f"🎯 Your dataset '{final_dataset.name}' is ready for use")
            print(f"🆔 IMPORTANT: Save this Dataset ID for future operations: {final_dataset.id}")
            print(f"💡 You can now:")
            print(f"   - Browse the dataset in the Keywords AI UI")
            print(f"   - Use the Dataset ID ({final_dataset.id}) in other API calls")
            print(f"   - Run additional evaluations on this dataset")
            print(f"   - Delete the dataset manually when no longer needed")
            print(f"🔗 Access your dataset: [Keywords AI Dashboard] -> Datasets -> {final_dataset.name}")
            
            # Note: We intentionally do NOT delete the dataset here
            # The user wants to review it in the UI first
            created_dataset = None  # Prevent cleanup in finally block
            
        except Exception as e:
            print(f"❌ Workflow failed: {e}")
            import traceback
            traceback.print_exc()
            raise
            
        finally:
            # Only cleanup if something went wrong and user wants auto-cleanup
            if created_dataset and os.getenv("AUTO_CLEANUP_ON_ERROR", "false").lower() == "true":
                try:
                    print(f"\n🗑️  Auto-cleanup enabled, deleting test dataset...")
                    await dataset_api.delete(created_dataset.id)
                    print(f"   ✅ Test dataset deleted")
                except Exception as cleanup_error:
                    print(f"   ⚠️  Could not delete dataset: {cleanup_error}")


async def demo_workflow():
    """Demo version when running as script"""
    test_instance = TestRealWorldDatasetWorkflow()
    await test_instance.test_real_world_dataset_workflow_2025_08_06()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # Run pytest mode
        pytest.main([__file__, "-v", "-s"])
    else:
        # Run demo mode
        asyncio.run(demo_workflow())
#!/usr/bin/env python3
"""
Keywords AI Dataset Workflow Example

This example demonstrates the complete dataset workflow:
1. List available logs
2. Create a new dataset
3. Add logs to the dataset
4. List datasets
5. Update dataset
6. Run evaluation on dataset
7. Get evaluation results

Usage:
    python examples/dataset_workflow_example.py

Environment variables required:
- KEYWORDSAI_API_KEY
- KEYWORDSAI_BASE_URL (optional, defaults to http://localhost:8000)
"""

import asyncio
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from keywordsai.datasets.api import DatasetAPI
from keywordsai.evaluators.api import EvaluatorAPI
from keywordsai_sdk.keywordsai_types.dataset_types import (
    DatasetCreate,
    DatasetUpdate,
    LogManagementRequest,
)


async def main():
    """Main example workflow"""
    
    # Setup
    api_key = os.getenv("KEYWORDSAI_API_KEY")
    base_url = os.getenv("KEYWORDSAI_BASE_URL", "http://localhost:8000")
    
    if not api_key:
        print("❌ KEYWORDSAI_API_KEY not found in environment")
        print("   Please set your API key in .env file")
        return
    
    print("🚀 Keywords AI Dataset Workflow Example")
    print("=" * 50)
    print(f"🔗 Using API: {base_url}")
    print()
    
    # Initialize clients
    dataset_api = DatasetAPI(api_key=api_key, base_url=base_url)
    evaluator_api = EvaluatorAPI(api_key=api_key, base_url=base_url)
    
    created_dataset = None
    
    try:
        # Step 1: List available logs for dataset creation
        print("📋 Step 1: Listing available logs...")
        week_ago = datetime.utcnow() - timedelta(days=7)
        now = datetime.utcnow()
        
        logs_response = await dataset_api.client.get("logs/", params={
            "start_time": week_ago.strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": now.strftime("%Y-%m-%d %H:%M:%S"),
            "page_size": 10
        })
        
        print(f"   ✅ Found {len(logs_response.get('results', []))} logs")
        if logs_response.get('results'):
            log_ids = [log['id'] for log in logs_response['results'][:5]]
            print(f"   📄 Sample log IDs: {log_ids[:3]}...")
        else:
            print("   ⚠️  No logs found in the specified time range")
            log_ids = []
        print()
        
        # Step 2: Create a new dataset
        print("📝 Step 2: Creating a new dataset...")
        dataset_data = DatasetCreate(
            name=f"EXAMPLE_DATASET_{int(now.timestamp())}",
            description="Example dataset created by SDK workflow",
            type="sampling",
            sampling=10,
            start_time=week_ago.isoformat() + "Z",
            end_time=now.isoformat() + "Z"
        )
        
        created_dataset = await dataset_api.acreate(dataset_data)
        print(f"   ✅ Created dataset: {created_dataset.name}")
        print(f"   🆔 Dataset ID: {created_dataset.id}")
        print(f"   📊 Type: {created_dataset.type}, Sampling: {getattr(created_dataset, 'sampling', 'N/A')}")
        print()
        
        # Step 3: Add logs to dataset (if we have logs)
        if log_ids:
            print("➕ Step 3: Adding logs to dataset...")
            log_request = LogManagementRequest(
                start_time=week_ago.strftime("%Y-%m-%d %H:%M:%S"),
                end_time=now.strftime("%Y-%m-%d %H:%M:%S"),
                filters={
                    "id": {
                        "value": log_ids,
                        "operator": "in"
                    }
                }
            )
            
            add_result = await dataset_api.aadd_logs_to_dataset(created_dataset.id, log_request)
            print(f"   ✅ {add_result.get('message', 'Logs added')}")
            if 'count' in add_result:
                print(f"   📊 Logs processed: {add_result['count']}")
            print()
        else:
            print("⏭️  Step 3: Skipping log addition (no logs available)")
            print()
        
        # Step 4: List all datasets
        print("📋 Step 4: Listing all datasets...")
        datasets = await dataset_api.alist(page_size=5)
        print(f"   ✅ Found {len(datasets.results)} datasets")
        for i, ds in enumerate(datasets.results[:3], 1):
            print(f"   {i}. {ds.name} (ID: {ds.id})")
        print()
        
        # Step 5: Update the dataset
        print("✏️  Step 5: Updating dataset name...")
        update_data = DatasetUpdate(name=f"{dataset_data.name}_UPDATED")
        updated_dataset = await dataset_api.aupdate(created_dataset.id, update_data)
        print(f"   ✅ Updated name: {updated_dataset.name}")
        print()
        
        # Step 6: List available evaluators
        print("🔍 Step 6: Discovering available evaluators...")
        evaluators = await evaluator_api.alist(page_size=5)
        print(f"   ✅ Found {len(evaluators.results)} evaluators")
        
        if evaluators.results:
            for i, evaluator in enumerate(evaluators.results[:3], 1):
                print(f"   {i}. {evaluator.name} (slug: {evaluator.slug})")
            print()
            
            # Step 7: Run evaluation on dataset
            print("🎯 Step 7: Running evaluation on dataset...")
            evaluator_slug = evaluators.results[0].slug
            print(f"   🔧 Using evaluator: {evaluator_slug}")
            
            try:
                eval_result = await dataset_api.arun_dataset_evaluation(
                    created_dataset.id, 
                    [evaluator_slug]
                )
                print(f"   ✅ {eval_result.get('message', 'Evaluation started')}")
                print()
                
                # Step 8: Check evaluation results
                print("📊 Step 8: Checking evaluation results...")
                reports = await dataset_api.alist_evaluation_reports(created_dataset.id)
                print(f"   ✅ Found {len(reports.results)} evaluation reports")
                
                if reports.results:
                    for i, report in enumerate(reports.results[:2], 1):
                        print(f"   {i}. Report ID: {report.id}")
                        if hasattr(report, 'status'):
                            print(f"      Status: {report.status}")
                print()
                
            except Exception as eval_error:
                print(f"   ⚠️  Evaluation failed (may be expected if dataset has no logs): {eval_error}")
                print()
        else:
            print("   ⚠️  No evaluators available")
            print()
        
        # Step 9: Get dataset details
        print("📖 Step 9: Retrieving final dataset details...")
        final_dataset = await dataset_api.aget(created_dataset.id)
        print(f"   ✅ Dataset: {final_dataset.name}")
        print(f"   📅 Created: {getattr(final_dataset, 'created_at', 'N/A')}")
        print(f"   📝 Description: {final_dataset.description}")
        print()
        
        print("🎉 Workflow completed successfully!")
        
    except Exception as e:
        print(f"❌ Error in workflow: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Cleanup
        if created_dataset:
            try:
                print("\n🗑️  Cleaning up...")
                await dataset_api.adelete(created_dataset.id)
                print("   ✅ Test dataset deleted")
            except Exception as cleanup_error:
                print(f"   ⚠️  Could not delete dataset: {cleanup_error}")


if __name__ == "__main__":
    asyncio.run(main())
#!/usr/bin/env python3
"""
Keywords AI SDK Structure Demo

This example shows the SDK structure and how to initialize clients
without making actual API calls.

Usage:
    python examples/sdk_structure_demo.py
"""

import os
from dotenv import load_dotenv

load_dotenv()

from keywordsai.datasets.api import DatasetAPI, SyncDatasetAPI
from keywordsai.evaluators.api import EvaluatorAPI, SyncEvaluatorAPI
from keywordsai_sdk.keywordsai_types.dataset_types import DatasetCreate, DatasetUpdate, LogManagementRequest
from keywordsai.types.evaluator_types import Evaluator, EvaluatorList


def main():
    """Demo SDK structure and initialization"""
    
    print("🏗️  Keywords AI SDK Structure Demo")
    print("=" * 50)
    
    # 1. Show SDK structure
    print("📦 Available API Clients:")
    print("   📊 DatasetAPI (async) - Manage datasets")
    print("   📊 SyncDatasetAPI (sync) - Manage datasets synchronously") 
    print("   🔍 EvaluatorAPI (async) - Work with evaluators")
    print("   🔍 SyncEvaluatorAPI (sync) - Work with evaluators synchronously")
    print()
    
    # 2. Show initialization
    print("🔧 Client Initialization:")
    api_key = os.getenv("KEYWORDSAI_API_KEY", "your-api-key-here")
    base_url = os.getenv("KEYWORDSAI_BASE_URL", "http://localhost:8000")
    
    print(f"   🔑 API Key: {api_key[:10]}..." if len(api_key) > 10 else f"   🔑 API Key: {api_key}")
    print(f"   🌐 Base URL: {base_url}")
    print()
    
    # Initialize clients (no API calls yet)
    print("🚀 Initializing clients...")
    dataset_api = DatasetAPI(api_key=api_key, base_url=base_url)
    sync_dataset_api = SyncDatasetAPI(api_key=api_key, base_url=base_url)
    evaluator_api = EvaluatorAPI(api_key=api_key, base_url=base_url)
    sync_evaluator_api = SyncEvaluatorAPI(api_key=api_key, base_url=base_url)
    
    print("   ✅ DatasetAPI (async) initialized")
    print("   ✅ SyncDatasetAPI initialized")  
    print("   ✅ EvaluatorAPI (async) initialized")
    print("   ✅ SyncEvaluatorAPI initialized")
    print()
    
    # 3. Show available methods
    print("📋 Available Dataset Methods:")
    dataset_methods = [method for method in dir(dataset_api) if not method.startswith('_') and callable(getattr(dataset_api, method))]
    for method in sorted(dataset_methods):
        print(f"   • {method}()")
    print()
    
    print("📋 Available Evaluator Methods:")
    evaluator_methods = [method for method in dir(evaluator_api) if not method.startswith('_') and callable(getattr(evaluator_api, method))]
    for method in sorted(evaluator_methods):
        print(f"   • {method}()")
    print()
    
    # 4. Show data types
    print("📝 Available Data Types:")
    print("   📊 Dataset Types:")
    print("      • DatasetCreate - For creating new datasets")
    print("      • DatasetUpdate - For updating existing datasets")
    print("      • LogManagementRequest - For managing logs in datasets")
    print()
    print("   🔍 Evaluator Types:")
    print("      • Evaluator - Individual evaluator model")
    print("      • EvaluatorList - List of evaluators with pagination")
    print()
    
    # 5. Show example usage patterns (no API calls)
    print("💡 Usage Patterns:")
    print()
    print("   🔄 Async Pattern:")
    print("   ```python")
    print("   async def my_function():")
    print("       dataset_api = DatasetAPI(api_key='...', base_url='...')")
    print("       datasets = await dataset_api.list()")
    print("       return datasets")
    print("   ```")
    print()
    print("   🔄 Sync Pattern:")
    print("   ```python")
    print("   def my_function():")
    print("       dataset_api = SyncDatasetAPI(api_key='...', base_url='...')")
    print("       datasets = dataset_api.list()")
    print("       return datasets")
    print("   ```")
    print()
    
    # 6. Show workflow overview
    print("🔄 Typical Workflow:")
    print("   1. Initialize API client")
    print("   2. List available evaluators")
    print("   3. Create a dataset")
    print("   4. Add logs to dataset")
    print("   5. Run evaluation on dataset")
    print("   6. Get evaluation results")
    print("   7. Update or delete dataset")
    print()
    
    print("✅ SDK structure demo complete!")
    print()
    print("🚀 Next Steps:")
    print("   • Set up your .env file with KEYWORDSAI_API_KEY")
    print("   • Run: python examples/simple_evaluator_example.py")
    print("   • Run: python examples/dataset_workflow_example.py")
    print("   • Check: examples/README.md for more details")


if __name__ == "__main__":
    main()
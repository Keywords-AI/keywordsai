#!/usr/bin/env python3
"""
Respan SDK Structure Demo

This example shows the SDK structure and how to initialize clients
without making actual API calls.

Usage:
    python examples/sdk_structure_demo.py
"""

import os
from dotenv import load_dotenv

load_dotenv()

from respan.datasets.api import DatasetAPI, SyncDatasetAPI
from respan.evaluators.api import EvaluatorAPI, SyncEvaluatorAPI
from respan.prompts.api import PromptAPI, SyncPromptAPI
from respan_sdk.respan_types.dataset_types import DatasetCreate, DatasetUpdate, LogManagementRequest
from respan.types.evaluator_types import Evaluator, EvaluatorList
from respan_sdk.respan_types.prompt_types import Prompt, PromptVersion


def main():
    """Demo SDK structure and initialization"""
    
    print("🏗️  Respan SDK Structure Demo")
    print("=" * 50)
    
    # 1. Show SDK structure
    print("📦 Available API Clients:")
    print("   📊 DatasetAPI (async) - Manage datasets")
    print("   📊 SyncDatasetAPI (sync) - Manage datasets synchronously") 
    print("   🔍 EvaluatorAPI (async) - Work with evaluators")
    print("   🔍 SyncEvaluatorAPI (sync) - Work with evaluators synchronously")
    print("   📝 PromptAPI (async) - Manage prompts and versions")
    print("   📝 SyncPromptAPI (sync) - Manage prompts and versions synchronously")
    print()
    
    # 2. Show initialization
    print("🔧 Client Initialization:")
    api_key = os.getenv("RESPAN_API_KEY", "your-api-key-here")
    base_url = os.getenv("RESPAN_BASE_URL", "http://localhost:8000")
    
    print(f"   🔑 API Key: {api_key[:10]}..." if len(api_key) > 10 else f"   🔑 API Key: {api_key}")
    print(f"   🌐 Base URL: {base_url}")
    print()
    
    # Initialize clients (no API calls yet)
    print("🚀 Initializing clients...")
    dataset_api = DatasetAPI(api_key=api_key, base_url=base_url)
    sync_dataset_api = SyncDatasetAPI(api_key=api_key, base_url=base_url)
    evaluator_api = EvaluatorAPI(api_key=api_key, base_url=base_url)
    sync_evaluator_api = SyncEvaluatorAPI(api_key=api_key, base_url=base_url)
    prompt_api = PromptAPI(api_key=api_key, base_url=base_url)
    sync_prompt_api = SyncPromptAPI(api_key=api_key, base_url=base_url)
    
    print("   ✅ DatasetAPI (async) initialized")
    print("   ✅ SyncDatasetAPI initialized")  
    print("   ✅ EvaluatorAPI (async) initialized")
    print("   ✅ SyncEvaluatorAPI initialized")
    print("   ✅ PromptAPI (async) initialized")
    print("   ✅ SyncPromptAPI initialized")
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
    
    # 4. Show available prompt methods
    print("📋 Available Prompt Methods:")
    prompt_methods = [method for method in dir(prompt_api) if not method.startswith('_') and callable(getattr(prompt_api, method))]
    for method in prompt_methods[:8]:  # Show first 8 methods
        print(f"      • {method}")
    print(f"      ... and {len(prompt_methods) - 8} more methods")
    print()

    # 5. Show data types
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
    print("   📝 Prompt Types:")
    print("      • Prompt - Individual prompt model")
    print("      • PromptVersion - Prompt version model")
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
    print("🔄 Typical Workflows:")
    print()
    print("   📊 Dataset Workflow:")
    print("      1. Initialize API client")
    print("      2. List available evaluators")
    print("      3. Create a dataset")
    print("      4. Add logs to dataset")
    print("      5. Run evaluation on dataset")
    print("      6. Get evaluation results")
    print()
    print("   📝 Prompt Workflow:")
    print("      1. Initialize PromptAPI client")
    print("      2. Create a new prompt")
    print("      3. Create versions with different configurations")
    print("      4. List and retrieve prompts and versions")
    print("      5. Update prompt and version properties")
    print()
    
    print("✅ SDK structure demo complete!")
    print()
    print("🚀 Next Steps:")
    print("   • Set up your .env file with RESPAN_API_KEY")
    print("   • Run: python examples/simple_evaluator_example.py")
    print("   • Run: python examples/dataset_workflow_example.py")
    print("   • Check: examples/README.md for more details")


if __name__ == "__main__":
    main()
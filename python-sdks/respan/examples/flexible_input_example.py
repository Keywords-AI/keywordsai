"""
Example demonstrating flexible input options for Keywords AI Python SDK

This example shows how you can use either dictionaries or Pydantic models
as input to all API methods. This makes the SDK much more user-friendly
by eliminating the need to import and construct complex nested Pydantic types.
"""

import asyncio
from keywordsai import (
    ExperimentAPI,
    DatasetAPI, 
    LogAPI,
    # You can still import the Pydantic types if you want to use them
    ExperimentCreate,
    DatasetCreate,
)
from keywordsai.prompts.api import PromptAPI
from keywordsai_sdk.keywordsai_types.prompt_types import Prompt, PromptVersion


async def main():
    """Demonstrate flexible input options across all APIs"""
    
    # Initialize clients
    experiment_client = ExperimentAPI(api_key="your-api-key")
    dataset_client = DatasetAPI(api_key="your-api-key") 
    log_client = LogAPI(api_key="your-api-key")
    prompt_client = PromptAPI(api_key="your-api-key")
    
    print("=== EXPERIMENTS API - Flexible Input Examples ===\n")
    
    # Option 1: Using dictionaries (much simpler!)
    print("1. Creating experiment with dictionary input:")
    experiment_dict = {
        "name": "My Simple Experiment",
        "description": "Created using a simple dictionary",
        "columns": [
            {
                "model": "gpt-3.5-turbo",
                "name": "Version A",
                "temperature": 0.7,
                "max_completion_tokens": 256,
                "prompt_messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "{{user_input}}"}
                ]
            }
        ],
        "rows": [
            {
                "input": {"user_input": "What is the weather like?"}
            }
        ]
    }
    
    try:
        # This now works with a simple dictionary!
        experiment = await experiment_client.acreate(experiment_dict)
        print(f"✓ Created experiment: {experiment.name}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Option 2: Using Pydantic models (still supported)
    print("\n2. Creating experiment with Pydantic model:")
    try:
        from keywordsai.types.experiment_types import ExperimentColumnType, ExperimentRowType
        
        experiment_pydantic = ExperimentCreate(
            name="My Pydantic Experiment", 
            description="Created using Pydantic model",
            columns=[
                ExperimentColumnType(
                    model="gpt-4",
                    name="Version B",
                    temperature=0.3,
                    max_completion_tokens=200,
                    prompt_messages=[
                        {"role": "system", "content": "You are a formal assistant."}
                    ]
                )
            ],
            rows=[
                ExperimentRowType(
                    input={"user_input": "Explain quantum computing"}
                )
            ]
        )
        
        experiment = await experiment_client.acreate(experiment_pydantic)
        print(f"✓ Created experiment: {experiment.name}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\n=== DATASETS API - Flexible Input Examples ===\n")
    
    # Option 1: Using dictionaries for dataset creation
    print("1. Creating dataset with dictionary input:")
    dataset_dict = {
        "name": "My Simple Dataset",
        "description": "Created using a simple dictionary",
        "type": "sampling",
        "sampling": 100,
        "start_time": "2024-01-01T00:00:00Z",
        "end_time": "2024-01-02T00:00:00Z"
    }
    
    try:
        dataset = await dataset_client.acreate(dataset_dict)
        print(f"✓ Created dataset: {dataset.name}")
        
        # Adding logs with dictionary
        print("\n2. Adding logs to dataset with dictionary input:")
        log_request_dict = {
            "start_time": "2024-01-01 00:00:00",
            "end_time": "2024-01-01 23:59:59", 
            "filters": {
                "status": {"value": "success", "operator": "equals"},
                "model": {"value": "gpt-4", "operator": "equals"}
            }
        }
        
        result = await dataset_client.aadd_logs_to_dataset(dataset.id, log_request_dict)
        print(f"✓ Added logs to dataset: {result}")
        
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\n=== LOGS API - Flexible Input Examples ===\n")
    
    # Option 1: Using dictionaries for log creation
    print("1. Creating log with dictionary input:")
    log_dict = {
        "model": "gpt-4",
        "input": "What is machine learning?",
        "output": "Machine learning is a subset of artificial intelligence...",
        "status_code": 200,
        "custom_identifier": "ml_qa_001"
    }
    
    try:
        response = await log_client.acreate(log_dict)
        print(f"✓ Created log: {response}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Option 2: Using Pydantic model (still supported)
    print("\n2. Creating log with Pydantic model:")
    try:
        from keywordsai.types.log_types import KeywordsAILogParams
        
        log_pydantic = KeywordsAILogParams(
            model="gpt-3.5-turbo",
            input="How does photosynthesis work?",
            output="Photosynthesis is the process by which plants...",
            status_code=200,
            custom_identifier="bio_qa_001"
        )
        
        response = await log_client.acreate(log_pydantic)
        print(f"✓ Created log: {response}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\n=== SYNCHRONOUS USAGE (Same Flexibility) ===\n")
    
    # All the same flexibility works with synchronous methods too
    print("Creating experiment synchronously with dictionary:")
    sync_experiment_dict = {
        "name": "Sync Experiment",
        "description": "Created synchronously with dictionary",
        "columns": [
            {
                "model": "gpt-3.5-turbo",
                "name": "Sync Column",
                "temperature": 0.5,
                "max_completion_tokens": 150,
                "prompt_messages": [
                    {"role": "user", "content": "{{prompt}}"}
                ]
            }
        ]
    }
    
    try:
        # Note: no 'await' needed for synchronous methods
        sync_experiment = experiment_client.create(sync_experiment_dict)
        print(f"✓ Created sync experiment: {sync_experiment.name}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\n=== BENEFITS OF THIS APPROACH ===")
    print("✓ No need to import complex nested Pydantic types")
    print("✓ Simple dictionary syntax that's easy to read and write") 
    print("✓ Still get full validation and error handling")
    print("✓ Backward compatible - existing Pydantic code still works")
    print("✓ IDE autocomplete and type hints still work")
    print("✓ Much more user-friendly for quick prototyping")


async def prompt_examples():
    """Demonstrate flexible input for Prompt API"""
    prompt_client = PromptAPI(api_key="your-api-key")
    
    print("=== PROMPTS API - Flexible Input Examples ===\n")
    
    # Option 1: Dictionary input for prompt creation
    print("1. Creating prompt with dictionary input:")
    prompt_dict = {
        "name": "Customer Support Bot",
        "description": "AI assistant for customer support"
    }
    print(f"Dictionary: {prompt_dict}")
    # result = await prompt_client.acreate(prompt_dict)
    print("✅ Would create prompt using dictionary\n")
    
    # Option 2: Pydantic model for prompt creation
    print("2. Creating prompt with Pydantic model:")
    prompt_model = Prompt(
        name="Customer Support Bot", 
        description="AI assistant for customer support"
    )
    print(f"Pydantic model: {prompt_model}")
    # result = await prompt_client.acreate(prompt_model)
    print("✅ Would create prompt using Pydantic model\n")
    
    # Option 3: Dictionary input for prompt version
    print("3. Creating prompt version with dictionary input:")
    version_dict = {
        "description": "Version 1 with basic configuration",
        "messages": [
            {"role": "system", "content": "You are a helpful customer support assistant."},
            {"role": "user", "content": "{{customer_question}}"}
        ],
        "model": "gpt-4o-mini",
        "temperature": 0.7,
        "max_tokens": 2048,
        "variables": {"customer_question": "Customer's inquiry"}
    }
    print(f"Dictionary: {version_dict}")
    # result = await prompt_client.acreate_version("prompt-id", version_dict)
    print("✅ Would create version using dictionary\n")
    
    # Option 4: Pydantic model for prompt version
    print("4. Creating prompt version with Pydantic model:")
    from datetime import datetime, timezone
    version_model = PromptVersion(
        prompt_version_id="version-001",
        description="Version 1 with basic configuration",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        version=1,
        messages=[
            {"role": "system", "content": "You are a helpful customer support assistant."},
            {"role": "user", "content": "{{customer_question}}"}
        ],
        model="gpt-4o-mini",
        temperature=0.7,
        max_tokens=2048,
        variables={"customer_question": "Customer's inquiry"},
        parent_prompt="prompt-id"
    )
    print(f"Pydantic model: {version_model}")
    # result = await prompt_client.acreate_version("prompt-id", version_model)
    print("✅ Would create version using Pydantic model\n")


if __name__ == "__main__":
    # Run the async example
    asyncio.run(main())
    
    print("\n" + "="*60)
    
    # Run prompt examples
    asyncio.run(prompt_examples())
    
    print("\n" + "="*60)
    print("QUICK COMPARISON - Before vs After")
    print("="*60)
    
    print("\nBEFORE (Complex imports and nested types):")
    print("""
from keywordsai import ExperimentAPI
from keywordsai.types.experiment_types import (
    ExperimentCreate, 
    ExperimentColumnType,
    ExperimentRowType
)

client = ExperimentAPI(api_key="key")
experiment = ExperimentCreate(
    name="Test",
    columns=[
        ExperimentColumnType(
            model="gpt-4",
            name="Version A", 
            temperature=0.7,
            prompt_messages=[
                {"role": "system", "content": "You are helpful."}
            ]
        )
    ],
    rows=[
        ExperimentRowType(input={"prompt": "Hello"})
    ]
)
result = client.create(experiment)
""")
    
    print("\nAFTER (Simple dictionary syntax):")
    print("""
from keywordsai import ExperimentAPI

client = ExperimentAPI(api_key="key")
experiment = {
    "name": "Test",
    "columns": [{
        "model": "gpt-4",
        "name": "Version A",
        "temperature": 0.7,
        "prompt_messages": [
            {"role": "system", "content": "You are helpful."}
        ]
    }],
    "rows": [
        {"input": {"prompt": "Hello"}}
    ]
}
result = client.create(experiment)  # Same result, much simpler!
""")

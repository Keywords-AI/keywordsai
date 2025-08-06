#!/usr/bin/env python3
"""
Experiment API Workflow Example

This example demonstrates how to use the Keywords AI Experiment API to:
1. Create an experiment with columns and rows
2. Add more rows and columns
3. Run the experiment
4. Run evaluations

Environment variables required:
- KEYWORDSAI_API_KEY
- KEYWORDSAI_BASE_URL (optional, defaults to production)

Usage:
    python examples/experiment_workflow_example.py
"""

import os
import asyncio
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from keywordsai import (
    ExperimentAPI,
    ExperimentCreate,
    ExperimentColumnType,
    ExperimentRowType,
    AddExperimentRowsRequest,
    AddExperimentColumnsRequest,
    RunExperimentRequest,
    RunExperimentEvalsRequest,
)


async def main():
    """Main workflow demonstration"""
    # Initialize the API client
    api_key = os.getenv("KEYWORDSAI_API_KEY")
    base_url = os.getenv("KEYWORDSAI_BASE_URL")  # Optional
    
    if not api_key:
        print("❌ KEYWORDSAI_API_KEY environment variable is required")
        return
    
    client = ExperimentAPI(api_key=api_key, base_url=base_url)
    print("✅ Experiment API client initialized")
    
    # Generate unique experiment name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    experiment_name = f"SDK_Example_Experiment_{timestamp}"
    
    try:
        # Step 1: Create an experiment with initial columns and rows
        print("\n🔬 Step 1: Creating experiment...")
        
        initial_column = ExperimentColumnType(
            model="gpt-3.5-turbo",
            name="Helpful Assistant",
            temperature=0.7,
            max_completion_tokens=200,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            prompt_messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant. Answer questions clearly and concisely."
                },
                {
                    "role": "user",
                    "content": "{{question}}"
                }
            ],
            tools=[],
            tool_choice="auto",
            response_format={"type": "text"}
        )
        
        initial_row = ExperimentRowType(
            input={"question": "What is artificial intelligence?"},
            ideal_output="AI is the simulation of human intelligence in machines."
        )
        
        experiment_data = ExperimentCreate(
            name=experiment_name,
            description="Example experiment demonstrating SDK capabilities",
            columns=[initial_column],
            rows=[initial_row]
        )
        
        experiment = await client.acreate(experiment_data)
        print(f"✅ Created experiment: {experiment.name} (ID: {experiment.id})")
        
        # Step 2: Add more test cases (rows)
        print("\n📝 Step 2: Adding more test cases...")
        
        new_rows = [
            ExperimentRowType(
                input={"question": "What is machine learning?"},
                ideal_output="ML is a subset of AI that learns from data."
            ),
            ExperimentRowType(
                input={"question": "Explain neural networks briefly."},
                ideal_output="Neural networks are computing systems inspired by biological neural networks."
            ),
            ExperimentRowType(
                input={"question": "What is the difference between AI and ML?"}
                # No ideal_output for this one
            )
        ]
        
        add_rows_request = AddExperimentRowsRequest(rows=new_rows)
        await client.aadd_rows(experiment.id, add_rows_request)
        print(f"✅ Added {len(new_rows)} test cases")
        
        # Step 3: Add another model configuration (column)
        print("\n🤖 Step 3: Adding another model configuration...")
        
        new_column = ExperimentColumnType(
            model="gpt-4",
            name="Expert Assistant",
            temperature=0.3,  # Lower temperature for more focused responses
            max_completion_tokens=250,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            prompt_messages=[
                {
                    "role": "system",
                    "content": "You are an expert technical assistant. Provide accurate, detailed explanations."
                },
                {
                    "role": "user",
                    "content": "{{question}}"
                }
            ],
            tools=[],
            tool_choice="auto",
            response_format={"type": "text"}
        )
        
        add_columns_request = AddExperimentColumnsRequest(columns=[new_column])
        await client.aadd_columns(experiment.id, add_columns_request)
        print("✅ Added GPT-4 configuration")
        
        # Step 4: Update experiment metadata
        print("\n✏️  Step 4: Updating experiment metadata...")
        
        from keywordsai import ExperimentUpdate
        update_data = ExperimentUpdate(
            name=f"{experiment_name}_Updated",
            description="Updated experiment description with more details about the SDK workflow"
        )
        updated_experiment = await client.aupdate(experiment.id, update_data)
        print(f"✅ Updated experiment name to: {updated_experiment.name}")
        
        # Step 5: Check the updated experiment
        print("\n🔍 Step 5: Checking experiment status...")
        
        final_experiment = await client.aget(experiment.id)
        print(f"📊 Experiment now has:")
        print(f"   - {len(final_experiment.columns)} columns (model configurations)")
        print(f"   - {len(final_experiment.rows)} rows (test cases)")
        print(f"   - Status: {final_experiment.status}")
        print(f"   - Name: {final_experiment.name}")
        print(f"   - Description: {final_experiment.description}")
        
        # Step 6: Run the experiment (optional - may take time)
        print("\n🚀 Step 6: Running experiment...")
        print("⚠️  Note: This will make API calls to generate responses and may take time")
        
        run_result = await client.arun_experiment(experiment.id)
        print("✅ Experiment run initiated")
        print(f"📋 Run status: {run_result}")
        
        # Step 7: Run evaluations (optional)
        print("\n📊 Step 7: Running evaluations...")
        print("⚠️  Note: This requires the experiment to have outputs")
        
        try:
            evals_request = RunExperimentEvalsRequest(
                evaluator_slugs=["is_english"]  # Basic evaluator
            )
            eval_result = await client.arun_experiment_evals(experiment.id, evals_request)
            print("✅ Evaluations initiated")
            print(f"📊 Evaluation status: {eval_result}")
        except Exception as e:
            print(f"⚠️  Evaluation skipped: {e}")
        
        # Step 8: List all experiments
        print("\n📋 Step 8: Listing experiments...")
        
        experiments = await client.alist(page_size=5)
        print(f"📊 Found {experiments.total} total experiments")
        print("Recent experiments:")
        for exp in experiments.experiments[:3]:
            print(f"   - {exp.name} (ID: {exp.id})")
        
        print(f"\n✅ Workflow completed successfully!")
        print(f"🔬 Experiment '{experiment.name}' is ready for analysis")
        print(f"🌐 You can view it in the Keywords AI dashboard")
        
    except Exception as e:
        print(f"❌ Error during workflow: {e}")
        return
    
    finally:
        # Optional: Clean up the test experiment
        # Uncomment the following lines if you want to auto-delete the test experiment
        # print(f"\n🧹 Cleaning up test experiment...")
        # await client.adelete(experiment.id)
        # print("✅ Test experiment deleted")
        pass


def sync_example():
    """Synchronous version of the workflow"""
    print("🔄 Running synchronous example...")
    
    api_key = os.getenv("KEYWORDSAI_API_KEY")
    base_url = os.getenv("KEYWORDSAI_BASE_URL")
    
    if not api_key:
        print("❌ KEYWORDSAI_API_KEY environment variable is required")
        return
    
    client = ExperimentAPI(api_key=api_key, base_url=base_url)
    
    # Simple synchronous workflow
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    column = ExperimentColumnType(
        model="gpt-3.5-turbo",
        name="Sync Test Column",
        temperature=0.5,
        max_completion_tokens=150,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        prompt_messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "{{input}}"}
        ],
        tools=[],
        tool_choice="auto",
        response_format={"type": "text"}
    )
    
    row = ExperimentRowType(
        input={"input": "Hello, how are you?"}
    )
    
    experiment_data = ExperimentCreate(
        name=f"SDK_Sync_Example_{timestamp}",
        description="Synchronous SDK example",
        columns=[column],
        rows=[row]
    )
    
    try:
        # Create experiment synchronously
        experiment = client.create(experiment_data)
        print(f"✅ Sync: Created experiment {experiment.name}")
        
        # List experiments synchronously
        experiments = client.list(page_size=3)
        print(f"✅ Sync: Listed {len(experiments.experiments)} experiments")
        
        # Get experiment synchronously
        retrieved = client.get(experiment.id)
        print(f"✅ Sync: Retrieved experiment {retrieved.name}")
        
        print("✅ Synchronous workflow completed!")
        
    except Exception as e:
        print(f"❌ Sync error: {e}")


if __name__ == "__main__":
    print("🚀 Keywords AI Experiment API Example")
    print("=====================================")
    
    # Run async example
    print("\n1️⃣  Running asynchronous workflow...")
    asyncio.run(main())
    
    print("\n" + "="*50)
    
    # Run sync example
    print("\n2️⃣  Running synchronous workflow...")
    sync_example()
    
    print("\n🎉 All examples completed!")
    print("\n💡 Tips:")
    print("   - Check the Keywords AI dashboard to see your experiments")
    print("   - Use the experiment results to compare model performance")
    print("   - Run evaluations to get automated scoring")
    print("   - Export results for further analysis")
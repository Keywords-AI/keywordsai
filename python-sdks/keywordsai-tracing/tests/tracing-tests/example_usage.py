#!/usr/bin/env python3
"""
Example usage of the new KeywordsAI OpenTelemetry implementation.

This script demonstrates how to use the new implementation that replaces Traceloop
with direct OpenTelemetry usage while maintaining the same API.
"""

import os
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the new implementation
from keywordsai_tracing import KeywordsAITelemetry, workflow, task, agent, tool
from keywordsai_tracing.contexts.span import keywordsai_span_attributes

# Initialize telemetry (same as before, but now uses OpenTelemetry directly)
telemetry = KeywordsAITelemetry(
    app_name="example-app",
    api_key=os.getenv("KEYWORDSAI_API_KEY", "test-key"),
    base_url=os.getenv("KEYWORDSAI_BASE_URL", "https://api.keywordsai.co/api"),
    is_enabled=True
)

print("🚀 KeywordsAI OpenTelemetry Example")
print("=" * 50)

# Example 1: Basic workflow with tasks
@workflow(name="data_processing_workflow")
def data_processing_workflow(data):
    """Main workflow that processes data through multiple tasks"""
    print(f"📊 Starting workflow with data: {data}")
    
    # Step 1: Validate data
    validated_data = validate_data_task(data)
    
    # Step 2: Transform data
    transformed_data = transform_data_task(validated_data)
    
    # Step 3: Save results
    result = save_results_task(transformed_data)
    
    return result

@task(name="validate_data")
def validate_data_task(data):
    """Validate input data"""
    print(f"✅ Validating data: {data}")
    if not data:
        raise ValueError("Data cannot be empty")
    return {"validated": True, "data": data}

@task(name="transform_data")
def transform_data_task(validated_data):
    """Transform the validated data"""
    print(f"🔄 Transforming data: {validated_data}")
    data = validated_data["data"]
    return {"transformed": True, "result": data.upper() if isinstance(data, str) else str(data)}

@task(name="save_results")
def save_results_task(transformed_data):
    """Save the transformed results"""
    print(f"💾 Saving results: {transformed_data}")
    return {"saved": True, "final_result": transformed_data["result"]}

# Example 2: AI Agent with tools
@agent(name="research_agent")
def research_agent(query):
    """AI agent that researches a topic using various tools"""
    print(f"🤖 Research agent processing query: {query}")
    
    # Use web search tool
    search_results = web_search_tool(query)
    
    # Use analysis tool
    analysis = analyze_results_tool(search_results)
    
    return analysis

@tool(name="web_search")
def web_search_tool(query):
    """Simulate web search"""
    print(f"🔍 Searching web for: {query}")
    return f"Search results for '{query}': Found 10 relevant articles"

@tool(name="analyze_results")
def analyze_results_tool(search_results):
    """Analyze search results"""
    print(f"📈 Analyzing: {search_results}")
    return f"Analysis complete: {search_results} - High relevance score"

# Example 3: Async workflow
@workflow(name="async_workflow")
async def async_workflow(items):
    """Async workflow that processes items concurrently"""
    print(f"⚡ Starting async workflow with {len(items)} items")
    
    # Process items concurrently
    tasks = [async_process_item(item) for item in items]
    results = await asyncio.gather(*tasks)
    
    return results

@task(name="async_process_item")
async def async_process_item(item):
    """Async task to process a single item"""
    print(f"🔄 Processing item: {item}")
    await asyncio.sleep(0.1)  # Simulate async work
    return f"Processed: {item}"

# Example 4: Using context manager for additional metadata
@workflow(name="context_workflow")
def context_workflow(user_id, session_id):
    """Workflow that uses context manager for additional tracing metadata"""
    with keywordsai_span_attributes(
        keywordsai_params={
            "trace_group_identifier": f"user_{user_id}_session_{session_id}",
            "user_id": user_id,
            "session_id": session_id
        },
        enable_content_tracing=True
    ):
        print(f"👤 Processing for user {user_id}, session {session_id}")
        return process_user_request(user_id, session_id)

@task(name="process_user_request")
def process_user_request(user_id, session_id):
    """Process a user request with context"""
    print(f"⚙️ Processing request for user {user_id}")
    return {"user_id": user_id, "session_id": session_id, "status": "completed"}

# Example 5: Error handling
@workflow(name="error_handling_workflow")
def error_handling_workflow():
    """Demonstrate error handling in spans"""
    try:
        failing_task()
    except Exception as e:
        print(f"❌ Caught error: {e}")
        return {"error": str(e), "handled": True}

@task(name="failing_task")
def failing_task():
    """Task that intentionally fails"""
    raise ValueError("This is a test error for demonstration")

def main():
    """Run all examples"""
    print("\n1️⃣ Basic Workflow Example")
    print("-" * 30)
    result1 = data_processing_workflow("hello world")
    print(f"Result: {result1}")
    
    print("\n2️⃣ AI Agent Example")
    print("-" * 30)
    result2 = research_agent("artificial intelligence trends")
    print(f"Result: {result2}")
    
    print("\n3️⃣ Async Workflow Example")
    print("-" * 30)
    items = ["item1", "item2", "item3"]
    result3 = asyncio.run(async_workflow(items))
    print(f"Result: {result3}")
    
    print("\n4️⃣ Context Manager Example")
    print("-" * 30)
    result4 = context_workflow(user_id="123", session_id="abc")
    print(f"Result: {result4}")
    
    print("\n5️⃣ Error Handling Example")
    print("-" * 30)
    result5 = error_handling_workflow()
    print(f"Result: {result5}")
    
    print("\n✅ All examples completed!")
    print("\n📊 Key Features Demonstrated:")
    print("  • Workflow and task decorators")
    print("  • Agent and tool decorators")
    print("  • Async/await support")
    print("  • Context manager for metadata")
    print("  • Error handling and exception recording")
    print("  • Direct OpenTelemetry integration")
    
    # Flush any remaining spans
    telemetry.flush()

if __name__ == "__main__":
    main() 
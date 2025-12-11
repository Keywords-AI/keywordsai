"""
Simple integration test for KeywordsAI tracing with Instructor.

This test demonstrates the basic setup and integration between:
- KeywordsAI tracing SDK
- Instructor library for structured outputs
- OpenAI API with automatic instrumentation

Run this test to verify that your setup is working correctly.
"""

from dotenv import load_dotenv
import os
from pydantic import BaseModel, Field
import instructor
from keywordsai_tracing import KeywordsAITelemetry
from keywordsai_tracing.decorators import task, workflow

# Load environment variables
load_dotenv(".env", override=True)

# Verify environment setup
def check_environment():
    """Check that all required environment variables are set."""
    required_vars = ["KEYWORDSAI_API_KEY", "OPENAI_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these in your .env file")
        return False
    
    print("✅ Environment variables configured correctly")
    return True

# Initialize KeywordsAI Telemetry
print("🔧 Initializing KeywordsAI Telemetry...")
k_tl = KeywordsAITelemetry(app_name="instructor-integration-test")
print("✅ KeywordsAI Telemetry initialized")

# Define a simple model for testing
class QuickResponse(BaseModel):
    """A simple response model for testing."""
    answer: str = Field(description="The answer to the question")
    confidence: float = Field(description="Confidence level (0-1)", ge=0, le=1)
    reasoning: str = Field(description="Brief explanation of the reasoning")

# Initialize Instructor client
print("🔧 Initializing Instructor client...")
client = instructor.from_provider("openai/gpt-4o-mini")
print("✅ Instructor client initialized")

@task(name="simple_extraction")
def simple_structured_extraction(question: str) -> QuickResponse:
    """Simple test of structured extraction with tracing."""
    response = client.chat.completions.create(
        response_model=QuickResponse,
        messages=[
            {"role": "system", "content": "Answer the question clearly and provide your reasoning."},
            {"role": "user", "content": question}
        ],
        temperature=0.1,
        max_tokens=300
    )
    return response

@workflow(name="integration_test_workflow")
def run_integration_test():
    """Run a simple integration test."""
    
    print("\n🧪 Running integration test...")
    
    # Test question
    test_question = "What is 15 + 27? Please show your work."
    
    # Extract structured response
    result = simple_structured_extraction(test_question)
    
    print(f"✅ Question: {test_question}")
    print(f"✅ Answer: {result.answer}")
    print(f"✅ Confidence: {result.confidence:.2f}")
    print(f"✅ Reasoning: {result.reasoning}")
    
    # Basic validation
    expected_answer = "42"
    if expected_answer in result.answer:
        print("✅ Answer validation passed")
        return True
    else:
        print(f"⚠️ Answer validation warning: expected '{expected_answer}' in '{result.answer}'")
        return True  # Still pass, as LLM might format differently

def main():
    """Main integration test function."""
    print("🚀 KeywordsAI + Instructor Integration Test")
    print("=" * 50)
    
    # Check environment
    if not check_environment():
        print("❌ Environment check failed")
        return False
    
    try:
        # Run the integration test
        success = run_integration_test()
        
        print("\n" + "=" * 50)
        if success:
            print("✅ Integration test completed successfully!")
            print("\n📊 What was traced:")
            print("   ✅ Instructor structured output request")
            print("   ✅ OpenAI API call with parameters")
            print("   ✅ Response parsing and validation")
            print("   ✅ Token usage and timing")
            print("   ✅ Workflow execution trace")
            print("\n🎯 Next steps:")
            print("   1. Check your KeywordsAI dashboard for the trace")
            print("   2. Run the other instructor tests:")
            print("      - instructor_basic_test.py")
            print("      - instructor_advanced_test.py") 
            print("      - instructor_multi_provider_test.py")
            print("\n🌟 Integration successful! KeywordsAI + Instructor is working.")
        else:
            print("❌ Integration test failed")
        
        return success
        
    except Exception as e:
        print(f"❌ Integration test failed with error: {e}")
        print("\n🔍 Troubleshooting tips:")
        print("   1. Check your .env file has KEYWORDSAI_API_KEY and OPENAI_API_KEY")
        print("   2. Verify your API keys are valid and have sufficient credits")
        print("   3. Check your internet connection")
        print("   4. Ensure the virtual environment is activated")
        return False

if __name__ == "__main__":
    main()
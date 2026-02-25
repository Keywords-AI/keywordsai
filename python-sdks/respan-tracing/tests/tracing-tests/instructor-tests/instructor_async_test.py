"""
Async Instructor test with Respan tracing.

This test investigates why async Instructor clients might not work properly
with Respan tracing and provides debugging information.
"""

import asyncio
from dotenv import load_dotenv
import os
from typing import List, Optional
from pydantic import BaseModel, Field
import instructor
from openai import AsyncOpenAI
from respan_tracing import RespanTelemetry
from respan_tracing.decorators import task, workflow

# Load environment variables
load_dotenv(".env", override=True)

# Initialize Respan Telemetry
print("🔧 Initializing Respan Telemetry...")
k_tl = RespanTelemetry(app_name="instructor-async-test", log_level="DEBUG")
print("✅ Respan Telemetry initialized")

# Define test models
class AsyncUser(BaseModel):
    """A user model for async testing."""
    name: str = Field(description="The user's full name")
    age: int = Field(description="The user's age in years", ge=0, le=150)
    email: Optional[str] = Field(description="The user's email address", default=None)
    occupation: Optional[str] = Field(description="The user's job or profession", default=None)

class AsyncAnalysis(BaseModel):
    """Analysis result for async testing."""
    summary: str = Field(description="Summary of the analysis")
    sentiment: str = Field(description="Sentiment: positive, negative, or neutral")
    confidence: float = Field(description="Confidence score (0-1)", ge=0, le=1)
    key_points: List[str] = Field(description="Key points identified", max_length=5)

# Test different async client initialization methods
print("\n🧪 Testing different async client initialization methods...")

# Method 1: Using instructor.from_provider (recommended)
print("1️⃣ Testing instructor.from_provider method...")
try:
    async_client_v1 = instructor.from_provider("openai/gpt-4o-mini")
    print("   ✅ instructor.from_provider worked")
except Exception as e:
    print(f"   ❌ instructor.from_provider failed: {e}")
    async_client_v1 = None

# Method 2: Using AsyncOpenAI + instructor.from_openai (the problematic one)
print("2️⃣ Testing AsyncOpenAI + instructor.from_openai method...")
try:
    async_openai_client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    async_client_v2 = instructor.from_openai(async_openai_client)
    print("   ✅ AsyncOpenAI + instructor.from_openai worked")
except Exception as e:
    print(f"   ❌ AsyncOpenAI + instructor.from_openai failed: {e}")
    async_client_v2 = None

# Method 3: Using instructor.apatch (alternative)
print("3️⃣ Testing instructor.apatch method...")
try:
    async_openai_raw = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    async_client_v3 = instructor.apatch(async_openai_raw)
    print("   ✅ instructor.apatch worked")
except Exception as e:
    print(f"   ❌ instructor.apatch failed: {e}")
    async_client_v3 = None

@task(name="async_user_extraction_v1")
async def extract_user_async_v1(text: str) -> Optional[AsyncUser]:
    """Extract user using instructor.from_provider method."""
    if not async_client_v1:
        print("   ⚠️ Skipping v1 test - client not available")
        return None
    
    try:
        user = await async_client_v1.chat.completions.create(
            response_model=AsyncUser,
            messages=[
                {"role": "system", "content": "Extract user information from the provided text."},
                {"role": "user", "content": text}
            ],
            temperature=0.1,
            max_tokens=500
        )
        return user
    except Exception as e:
        print(f"   ❌ V1 extraction failed: {e}")
        return None

@task(name="async_user_extraction_v2")
async def extract_user_async_v2(text: str) -> Optional[AsyncUser]:
    """Extract user using AsyncOpenAI + instructor.from_openai method."""
    if not async_client_v2:
        print("   ⚠️ Skipping v2 test - client not available")
        return None
    
    try:
        user = await async_client_v2.chat.completions.create(
            response_model=AsyncUser,
            messages=[
                {"role": "system", "content": "Extract user information from the provided text."},
                {"role": "user", "content": text}
            ],
            temperature=0.1,
            max_tokens=500
        )
        return user
    except Exception as e:
        print(f"   ❌ V2 extraction failed: {e}")
        return None

@task(name="async_user_extraction_v3")
async def extract_user_async_v3(text: str) -> Optional[AsyncUser]:
    """Extract user using instructor.apatch method."""
    if not async_client_v3:
        print("   ⚠️ Skipping v3 test - client not available")
        return None
    
    try:
        user = await async_client_v3.chat.completions.create(
            response_model=AsyncUser,
            messages=[
                {"role": "system", "content": "Extract user information from the provided text."},
                {"role": "user", "content": text}
            ],
            temperature=0.1,
            max_tokens=500
        )
        return user
    except Exception as e:
        print(f"   ❌ V3 extraction failed: {e}")
        return None

@task(name="async_analysis_test")
async def perform_async_analysis(text: str) -> Optional[AsyncAnalysis]:
    """Perform async analysis using the working client."""
    # Use whichever client is available
    client = async_client_v1 or async_client_v2 or async_client_v3
    
    if not client:
        print("   ❌ No async client available for analysis")
        return None
    
    try:
        analysis = await client.chat.completions.create(
            response_model=AsyncAnalysis,
            messages=[
                {"role": "system", "content": "Analyze the provided text for sentiment and key points."},
                {"role": "user", "content": text}
            ],
            temperature=0.2,
            max_tokens=600
        )
        return analysis
    except Exception as e:
        print(f"   ❌ Async analysis failed: {e}")
        return None

@workflow(name="async_instructor_comparison")
async def run_async_comparison_tests():
    """Run async tests with different client initialization methods."""
    
    print("\n=== Async Client Comparison Tests ===")
    
    test_text = """
    Sarah Chen is a 29-year-old data scientist working at Microsoft. 
    She has a PhD in Computer Science and specializes in machine learning.
    Her email is sarah.chen@microsoft.com and she leads the AI research team.
    """
    
    # Test all three methods
    print("\n🔍 Testing Method 1: instructor.from_provider")
    user_v1 = await extract_user_async_v1(test_text)
    if user_v1:
        print(f"   ✅ Extracted: {user_v1.name}, {user_v1.age}, {user_v1.occupation}")
    
    print("\n🔍 Testing Method 2: AsyncOpenAI + instructor.from_openai")
    user_v2 = await extract_user_async_v2(test_text)
    if user_v2:
        print(f"   ✅ Extracted: {user_v2.name}, {user_v2.age}, {user_v2.occupation}")
    
    print("\n🔍 Testing Method 3: instructor.apatch")
    user_v3 = await extract_user_async_v3(test_text)
    if user_v3:
        print(f"   ✅ Extracted: {user_v3.name}, {user_v3.age}, {user_v3.occupation}")
    
    # Test async analysis
    print("\n🔍 Testing Async Analysis")
    analysis_text = """
    This new software update is absolutely fantastic! The performance improvements are incredible,
    and the new features make everything so much easier to use. However, there are a few minor
    bugs that need to be fixed, but overall it's a great release.
    """
    
    analysis = await perform_async_analysis(analysis_text)
    if analysis:
        print(f"   ✅ Analysis: {analysis.sentiment} (confidence: {analysis.confidence:.2f})")
        print(f"   ✅ Key points: {', '.join(analysis.key_points)}")
    
    return {
        "v1_result": user_v1,
        "v2_result": user_v2,
        "v3_result": user_v3,
        "analysis": analysis
    }

@task(name="debug_async_instrumentation")
async def debug_async_instrumentation():
    """Debug async instrumentation issues."""
    
    print("\n🔍 Debugging Async Instrumentation...")
    
    # Check if OpenTelemetry async instrumentation is working
    from opentelemetry import trace
    tracer = trace.get_tracer(__name__)
    
    with tracer.start_as_current_span("debug_span") as span:
        span.set_attribute("test.async", True)
        print("   ✅ Manual span creation works")
        
        # Test if async context propagation works
        async def nested_async_function():
            current_span = trace.get_current_span()
            if current_span and current_span.is_recording():
                print("   ✅ Async context propagation works")
                current_span.set_attribute("nested.async", True)
                return True
            else:
                print("   ❌ Async context propagation failed")
                return False
        
        context_works = await nested_async_function()
        return context_works

@workflow(name="async_instructor_debug")
async def main():
    """Main async workflow for debugging Instructor integration."""
    print("🚀 Starting Async Instructor + Respan Tracing Debug")
    print("=" * 60)
    
    # Debug instrumentation first
    instrumentation_works = await debug_async_instrumentation()
    
    # Run comparison tests
    results = await run_async_comparison_tests()
    
    print("\n" + "=" * 60)
    print("📊 Async Test Results Summary:")
    print(f"   Instrumentation works: {'✅' if instrumentation_works else '❌'}")
    print(f"   Method 1 (from_provider): {'✅' if results['v1_result'] else '❌'}")
    print(f"   Method 2 (AsyncOpenAI + from_openai): {'✅' if results['v2_result'] else '❌'}")
    print(f"   Method 3 (apatch): {'✅' if results['v3_result'] else '❌'}")
    print(f"   Analysis: {'✅' if results['analysis'] else '❌'}")
    
    # Provide recommendations
    print("\n💡 Recommendations:")
    if results['v1_result']:
        print("   ✅ Use instructor.from_provider('openai/gpt-4o-mini') - WORKS")
    if results['v2_result']:
        print("   ✅ AsyncOpenAI + instructor.from_openai - WORKS")
    else:
        print("   ❌ AsyncOpenAI + instructor.from_openai - FAILED")
        print("      This might be due to:")
        print("      - OpenTelemetry async instrumentation issues")
        print("      - Context propagation problems")
        print("      - Instructor version compatibility")
    if results['v3_result']:
        print("   ✅ instructor.apatch - WORKS")
    else:
        print("   ❌ instructor.apatch - FAILED")
    
    print("\n🎯 Check your Respan dashboard for async traces")
    
    return results

def run_async_test():
    """Run the async test."""
    return asyncio.run(main())

if __name__ == "__main__":
    run_async_test()



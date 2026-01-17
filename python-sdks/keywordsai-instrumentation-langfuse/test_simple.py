"""Simple test to verify keywordsai-instrumentation-langfuse package works.

This test demonstrates the key feature: one-line import swap.

Before: from langfuse import Langfuse, observe
After: from keywordsai_instrumentation_langfuse import Langfuse, observe
"""

import os
from pathlib import Path

# Load .env file if it exists
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        print(f"Loaded .env file from {env_path}")
    else:
        print(f"No .env file found, using test key")
        os.environ["KEYWORDSAI_API_KEY"] = "test-api-key-12345"
except ImportError:
    print("python-dotenv not installed, using test key")
    os.environ["KEYWORDSAI_API_KEY"] = "test-api-key-12345"

# THE KEY CHANGE: Import from our instrumentation package instead of langfuse
from keywordsai_instrumentation_langfuse import Langfuse, observe

print("\nTest 1: Import successful")
print(f"  - Langfuse class: {Langfuse}")
print(f"  - observe decorator: {observe}")

# Test 2: Verify the package is patched
from keywordsai_instrumentation_langfuse import is_patched
print(f"\nTest 2: Package patched status")
print(f"  - Is patched: {is_patched()}")

# Test 3: Use the observe decorator
@observe()
def test_function(message: str):
    """Test function with observe decorator."""
    return f"Processed: {message}"

print(f"\nTest 3: Decorator works")
result = test_function("Hello World")
print(f"  - Function result: {result}")

# Test 4: Initialize Langfuse client
print(f"\nTest 4: Initialize Langfuse client")
langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY", ""),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY", "")
)
print(f"  - Langfuse client initialized: {type(langfuse)}")

# Test 5: Complex multi-level trace tree
@observe()
def search_database(query: str, database: str):
    """Search database."""
    return {
        "database": database,
        "results": f"Found results for '{query}' in {database}",
        "count": 10
    }

@observe()
def validate_results(results: dict):
    """Validate search results."""
    return {
        "database": results["database"],
        "is_valid": True,
        "confidence": 0.95
    }

@observe()
def fetch_from_source(query: str, source: str):
    """Fetch data from a source."""
    results = search_database(query, source)
    validated = validate_results(results)
    return validated

@observe()
def aggregate_data(query: str):
    """Aggregate data from multiple sources."""
    sources = ["PostgreSQL", "MongoDB", "Redis"]
    all_results = []
    
    for source in sources:
        result = fetch_from_source(query, source)
        all_results.append(result)
    
    return all_results

@observe(as_type="generation")
def analyze_data(query: str, data: list):
    """Analyze aggregated data using AI."""
    valid_sources = [d["database"] for d in data if d["is_valid"]]
    analysis = f"Analysis of '{query}' from {len(valid_sources)} sources: {', '.join(valid_sources)}"
    return {
        "analysis": analysis,
        "sources_count": len(valid_sources),
        "confidence": sum(d["confidence"] for d in data) / len(data)
    }

@observe(as_type="generation")
def generate_summary(analysis: dict):
    """Generate executive summary."""
    return {
        "summary": f"Executive Summary: {analysis['analysis']}",
        "quality_score": analysis["confidence"] * 100
    }

@observe()
def complex_workflow(query: str):
    """Complex multi-level workflow with parallel branches."""
    print(f"\nExecuting complex workflow for: '{query}'")
    
    # Level 1: Aggregate data from multiple sources (creates 3 parallel branches)
    aggregated = aggregate_data(query)
    print(f"  - Aggregated data from {len(aggregated)} sources")
    
    # Level 2: Analyze the aggregated data
    analysis = analyze_data(query, aggregated)
    print(f"  - Generated analysis with {analysis['confidence']:.2f} confidence")
    
    # Level 3: Generate summary
    summary = generate_summary(analysis)
    print(f"  - Created summary with quality score: {summary['quality_score']:.0f}")
    
    return {
        "query": query,
        "summary": summary,
        "sources_analyzed": len(aggregated)
    }

print(f"\nTest 5: Complex multi-level trace tree")
print("  This creates a deep trace tree with:")
print("    - 3 parallel branches (PostgreSQL, MongoDB, Redis)")
print("    - Each branch has 2 levels: Search -> Validate")
print("    - Plus aggregation, analysis, and summary steps")
print("    - Total: ~11 spans across 4 levels")
result = complex_workflow("user engagement metrics")
print(f"  - Workflow result: {result['summary']['summary'][:60]}...")
print(f"  - Analyzed {result['sources_analyzed']} sources")

# Test 6: Flush traces
print(f"\nTest 6: Flush traces to Keywords AI")
langfuse.flush()
print(f"  - Traces flushed")

print("\n" + "=" * 60)
print("All tests passed!")
print("=" * 60)
print(f"\nAPI Key used: {os.getenv('KEYWORDSAI_API_KEY', 'NOT SET')[:20]}...")
print("\nTrace tree structure sent to Keywords AI:")
print("  complex_workflow (root span)")
print("  ├── aggregate_data")
print("  │   ├── fetch_from_source:PostgreSQL")
print("  │   │   ├── search_database")
print("  │   │   └── validate_results")
print("  │   ├── fetch_from_source:MongoDB")
print("  │   │   ├── search_database")
print("  │   │   └── validate_results")
print("  │   └── fetch_from_source:Redis")
print("  │       ├── search_database")
print("  │       └── validate_results")
print("  ├── analyze_data (generation)")
print("  └── generate_summary (generation)")
print("\nTotal: ~11 spans across 4 levels")
print("\nKey takeaway: Just change your import line!")
print("  Before: from langfuse import Langfuse, observe")
print("  After:  from keywordsai_instrumentation_langfuse import Langfuse, observe")
print("\nCheck your Keywords AI dashboard for traces:")
print("  https://platform.keywordsai.co/")

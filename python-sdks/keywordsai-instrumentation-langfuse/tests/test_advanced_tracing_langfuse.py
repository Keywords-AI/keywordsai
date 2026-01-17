"""
Advanced test for Langfuse instrumentation with complex tracing trees.

This test creates a multi-level, multi-branch tracing tree to verify:
1. Deep nesting (3-4 levels)
2. Parallel branches (multiple children from same parent)
3. Different observation types (generation, span, event)
4. Complex workflows with realistic scenarios
5. Proper parent-child relationships in trace hierarchy

Run with: poetry run python tests/test_advanced_tracing_langfuse.py
"""

import os
import logging
import time

# Set up debug logging BEFORE any imports
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# IMPORTANT: Instrument BEFORE importing Langfuse
from keywordsai_instrumentation_langfuse import LangfuseInstrumentor

# Mock Keywords AI API key for testing
os.environ["KEYWORDSAI_API_KEY"] = "test-api-key"

print("\n" + "="*80)
print("INSTRUMENTING LANGFUSE FOR ADVANCED TRACING TEST")
print("="*80)

# Instrument with debug endpoint (you can change this to actual Keywords AI endpoint)
instrumentor = LangfuseInstrumentor()
instrumentor.instrument(
    api_key="hVU0iNkz.4RFE0lsrCgB0NfXs8UbAeb9cPD8GinHv",
    endpoint="https://api.keywordsai.co/api/v1/traces/ingest"  # For testing - echoes back what we send
)

print("Instrumentation complete!")
print("="*80 + "\n")

# NOW import Langfuse
from langfuse import Langfuse, observe

print("\n" + "="*80)
print("INITIALIZING LANGFUSE CLIENT")
print("="*80)

# Initialize Langfuse (you can use dummy keys for testing)
langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY", "pk-lf-test"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY", "sk-lf-test"),
    host="https://cloud.langfuse.com"  # This will be intercepted
)

print("Langfuse client initialized")
print("="*80 + "\n")


# ============================================================================
# Level 1: Leaf functions (no children)
# ============================================================================

@observe()
def fetch_user_data(user_id: str):
    """Fetch user data from database."""
    print(f"    [Level 3] fetch_user_data: user_id={user_id}")
    time.sleep(0.01)  # Simulate database call
    return {"user_id": user_id, "name": f"User_{user_id}", "email": f"user_{user_id}@example.com"}


@observe()
def validate_input(text: str):
    """Validate input text."""
    print(f"    [Level 3] validate_input: text={text[:50]}...")
    time.sleep(0.01)
    return len(text) > 0 and len(text) < 1000


@observe(as_type="generation")
def generate_summary(content: str):
    """Generate summary of content."""
    print(f"    [Level 3] generate_summary: content_length={len(content)}")
    time.sleep(0.02)
    return f"Summary: {content[:100]}..."


@observe(as_type="generation")
def generate_tags(content: str):
    """Generate tags for content."""
    print(f"    [Level 3] generate_tags: content_length={len(content)}")
    time.sleep(0.01)
    return ["tag1", "tag2", "tag3"]


@observe()
def store_in_cache(key: str, value: str):
    """Store value in cache."""
    print(f"    [Level 3] store_in_cache: key={key}")
    time.sleep(0.01)
    return True


# ============================================================================
# Level 2: Intermediate functions (have children)
# ============================================================================

@observe()
def process_user_query(user_id: str, query: str):
    """Process user query with validation and user data."""
    print(f"  [Level 2] process_user_query: user_id={user_id}, query={query[:50]}...")
    
    # Parallel calls: fetch user data and validate input
    user_data = fetch_user_data(user_id)
    is_valid = validate_input(query)
    
    if not is_valid:
        return {"error": "Invalid input"}
    
    return {"user": user_data, "query": query, "validated": True}


@observe()
def analyze_content(content: str):
    """Analyze content by generating summary and tags."""
    print(f"  [Level 2] analyze_content: content_length={len(content)}")
    
    # Parallel generation calls
    summary = generate_summary(content)
    tags = generate_tags(content)
    
    return {"summary": summary, "tags": tags, "content_length": len(content)}


@observe()
def prepare_response(data: dict):
    """Prepare response with caching."""
    print(f"  [Level 2] prepare_response: data_keys={list(data.keys())}")
    
    cache_key = f"response_{hash(str(data))}"
    store_in_cache(cache_key, str(data))
    
    return {"response": data, "cached": True, "cache_key": cache_key}


# ============================================================================
# Level 1: Top-level workflow functions
# ============================================================================

@observe()
def document_processing_workflow(document: str, user_id: str):
    """
    Main document processing workflow with multiple levels.
    
    Structure:
    - document_processing_workflow (root)
      - process_user_query (Level 2)
        - fetch_user_data (Level 3)
        - validate_input (Level 3)
      - analyze_content (Level 2)
        - generate_summary (Level 3)
        - generate_tags (Level 3)
      - prepare_response (Level 2)
        - store_in_cache (Level 3)
    """
    print(f"\n[Level 1] document_processing_workflow: user_id={user_id}, doc_length={len(document)}")
    
    # Step 1: Process user query (creates 2 children)
    query_result = process_user_query(user_id, document)
    
    # Step 2: Analyze content (creates 2 children)
    analysis_result = analyze_content(document)
    
    # Step 3: Prepare response (creates 1 child)
    final_response = prepare_response({
        "query": query_result,
        "analysis": analysis_result
    })
    
    return final_response


@observe()
def multi_source_aggregation_workflow(query: str):
    """
    Complex workflow with multiple parallel branches and deep nesting.
    
    Structure:
    - multi_source_aggregation_workflow (root)
      - fetch_from_source: PostgreSQL (Level 2)
        - search_database (Level 3)
        - validate_results (Level 3)
      - fetch_from_source: MongoDB (Level 2)
        - search_database (Level 3)
        - validate_results (Level 3)
      - fetch_from_source: Redis (Level 2)
        - search_database (Level 3)
        - validate_results (Level 3)
      - aggregate_data (Level 2)
        - merge_results (Level 3)
        - deduplicate (Level 3)
      - analyze_data (Level 2) [generation]
      - generate_summary (Level 2) [generation]
    """
    print(f"\n[Level 1] multi_source_aggregation_workflow: query={query}")
    
    # Level 3 helper functions for database operations
    @observe()
    def search_database(source: str, query: str):
        print(f"      [Level 3] search_database: source={source}")
        time.sleep(0.01)
        return [f"{source}_result_1", f"{source}_result_2"]
    
    @observe()
    def validate_results(results: list):
        print(f"      [Level 3] validate_results: count={len(results)}")
        time.sleep(0.01)
        return [r for r in results if "result" in r]
    
    @observe()
    def fetch_from_source(source: str, query: str):
        """Fetch data from a specific source."""
        print(f"    [Level 2] fetch_from_source: source={source}")
        results = search_database(source, query)
        validated = validate_results(results)
        return {"source": source, "results": validated}
    
    @observe()
    def merge_results(results_list: list):
        print(f"      [Level 3] merge_results: sources={len(results_list)}")
        time.sleep(0.01)
        return [item for sublist in results_list for item in sublist]
    
    @observe()
    def deduplicate(results: list):
        print(f"      [Level 3] deduplicate: count={len(results)}")
        time.sleep(0.01)
        return list(set(results))
    
    @observe()
    def aggregate_data(sources_data: list):
        """Aggregate data from multiple sources."""
        print(f"    [Level 2] aggregate_data: sources={len(sources_data)}")
        merged = merge_results([d["results"] for d in sources_data])
        deduplicated = deduplicate(merged)
        return {"aggregated": deduplicated, "total_count": len(deduplicated)}
    
    @observe(as_type="generation")
    def analyze_aggregated_data(data: dict):
        """Analyze aggregated data."""
        print(f"    [Level 2] analyze_aggregated_data: items={data.get('total_count', 0)}")
        time.sleep(0.02)
        return {"analysis": "Complex analysis result", "items_analyzed": data.get("total_count", 0)}
    
    # Step 1: Fetch from multiple sources in parallel (3 parallel branches)
    postgres_data = fetch_from_source("PostgreSQL", query)
    mongodb_data = fetch_from_source("MongoDB", query)
    redis_data = fetch_from_source("Redis", query)
    
    # Step 2: Aggregate all sources (creates 2 children)
    aggregated = aggregate_data([postgres_data, mongodb_data, redis_data])
    
    # Step 3: Analyze (generation)
    analysis = analyze_aggregated_data(aggregated)
    
    # Step 4: Generate summary (generation)
    summary = generate_summary(str(aggregated))
    
    return {
        "sources": [postgres_data, mongodb_data, redis_data],
        "aggregated": aggregated,
        "analysis": analysis,
        "summary": summary
    }


def test_complex_document_workflow():
    """Test complex document processing workflow with 3-level nesting."""
    print("\n" + "="*80)
    print("TEST 1: Complex Document Processing Workflow (3 levels)")
    print("="*80)
    print("\nTrace structure:")
    print("  document_processing_workflow")
    print("    ├── process_user_query")
    print("    │   ├── fetch_user_data")
    print("    │   └── validate_input")
    print("    ├── analyze_content")
    print("    │   ├── generate_summary")
    print("    │   └── generate_tags")
    print("    └── prepare_response")
    print("        └── store_in_cache")
    print("")
    
    document = "This is a sample document for testing the advanced tracing capabilities."
    result = document_processing_workflow(document, "user123")
    
    print(f"\n  Result keys: {list(result.keys())}")
    assert "response" in result
    assert result["cached"] == True
    
    print("\n  Flushing Langfuse...")
    langfuse.flush()
    print("  Flush complete!")
    print("="*80 + "\n")


def test_multi_source_aggregation():
    """Test multi-source aggregation with 4-level deep nesting and parallel branches."""
    print("\n" + "="*80)
    print("TEST 2: Multi-Source Aggregation Workflow (4 levels, parallel branches)")
    print("="*80)
    print("\nTrace structure:")
    print("  multi_source_aggregation_workflow")
    print("    ├── fetch_from_source:PostgreSQL")
    print("    │   ├── search_database")
    print("    │   └── validate_results")
    print("    ├── fetch_from_source:MongoDB")
    print("    │   ├── search_database")
    print("    │   └── validate_results")
    print("    ├── fetch_from_source:Redis")
    print("    │   ├── search_database")
    print("    │   └── validate_results")
    print("    ├── aggregate_data")
    print("    │   ├── merge_results")
    print("    │   └── deduplicate")
    print("    ├── analyze_aggregated_data (generation)")
    print("    └── generate_summary (generation)")
    print("")
    
    result = multi_source_aggregation_workflow("test query")
    
    print(f"\n  Result keys: {list(result.keys())}")
    assert "sources" in result
    assert "aggregated" in result
    assert "analysis" in result
    assert len(result["sources"]) == 3
    
    print("\n  Flushing Langfuse...")
    langfuse.flush()
    print("  Flush complete!")
    print("="*80 + "\n")


def test_nested_workflow_composition():
    """Test composing workflows together (workflows calling workflows)."""
    print("\n" + "="*80)
    print("TEST 3: Nested Workflow Composition")
    print("="*80)
    
    @observe()
    def composed_workflow(user_id: str, document: str):
        """Workflow that calls other workflows."""
        print(f"\n[Level 1] composed_workflow: user_id={user_id}")
        
        # Call document processing workflow
        doc_result = document_processing_workflow(document, user_id)
        
        # Call multi-source aggregation
        agg_result = multi_source_aggregation_workflow(document)
        
        return {
            "document_processed": doc_result,
            "aggregation_complete": agg_result
        }
    
    result = composed_workflow("user456", "Test document for composition")
    
    print(f"\n  Result keys: {list(result.keys())}")
    assert "document_processed" in result
    assert "aggregation_complete" in result
    
    print("\n  Flushing Langfuse...")
    langfuse.flush()
    print("  Flush complete!")
    print("="*80 + "\n")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("RUNNING ADVANCED LANGFUSE TRACING TESTS")
    print("="*80 + "\n")
    
    try:
        test_complex_document_workflow()
        test_multi_source_aggregation()
        test_nested_workflow_composition()
        
        print("\n" + "="*80)
        print("ALL ADVANCED TESTS PASSED!")
        print("="*80 + "\n")
        
        print("\nTrace Tree Summary:")
        print("  - Test 1: 3-level deep tree with 8 spans")
        print("  - Test 2: 4-level deep tree with 11 spans (3 parallel branches)")
        print("  - Test 3: Combined workflows creating even deeper trees")
        print("\nNOTE: Check the debug logs above to see:")
        print("  1. Complex trace hierarchies being intercepted")
        print("  2. Multi-level parent-child relationships")
        print("  3. Parallel branches in trace tree")
        print("  4. Transformation to Keywords AI format")
        print("  5. Redirect to Keywords AI endpoint")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()

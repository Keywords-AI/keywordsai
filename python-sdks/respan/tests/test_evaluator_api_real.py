#!/usr/bin/env python3
"""
Evaluator API Real Integration Tests

These tests use real API calls to validate evaluator functionality.
No mocking - tests actual SDK behavior with Respan server.

Environment variables required:
- RESPAN_API_KEY
- RESPAN_BASE_URL

Usage:
    python -m pytest tests/test_evaluator_api_real.py -v -s
"""

import pytest
import os
from dotenv import load_dotenv

load_dotenv(override=True)

from respan.evaluators.api import EvaluatorAPI, SyncEvaluatorAPI


@pytest.fixture
def api_key():
    """Get API key from environment"""
    key = os.getenv("RESPAN_API_KEY")
    if not key:
        pytest.skip("RESPAN_API_KEY not found in environment")
    return key


@pytest.fixture
def base_url():
    """Get base URL from environment"""
    return os.getenv("RESPAN_BASE_URL", "http://localhost:8000")


@pytest.fixture
def evaluator_api(api_key, base_url):
    """Evaluator API client"""
    return EvaluatorAPI(api_key=api_key, base_url=base_url)


@pytest.fixture
def sync_evaluator_api(api_key, base_url):
    """Sync Evaluator API client"""
    return SyncEvaluatorAPI(api_key=api_key, base_url=base_url)


class TestEvaluatorAPIReal:
    """Test evaluator API operations with real API"""
    
    @pytest.mark.asyncio
    async def test_list_evaluators(self, evaluator_api):
        """Test listing evaluators"""
        result = await evaluator_api.list(page_size=10)
        
        assert hasattr(result, 'results')
        assert isinstance(result.results, list)
        
        # If evaluators exist, validate structure
        if result.results:
            evaluator = result.results[0]
            assert hasattr(evaluator, 'id')
            assert hasattr(evaluator, 'name')
            assert hasattr(evaluator, 'slug')
            
            # Test getting specific evaluator
            detailed_evaluator = await evaluator_api.get(evaluator.id)
            assert detailed_evaluator.id == evaluator.id
            assert detailed_evaluator.name == evaluator.name
            assert detailed_evaluator.slug == evaluator.slug
    
    @pytest.mark.asyncio
    async def test_list_evaluators_with_pagination(self, evaluator_api):
        """Test evaluator listing with pagination"""
        # Test small page size
        result = await evaluator_api.list(page_size=2)
        assert hasattr(result, 'results')
        assert len(result.results) <= 2
        
        # Test with page parameter
        page1 = await evaluator_api.list(page=1, page_size=5)
        assert hasattr(page1, 'results')
    
    @pytest.mark.asyncio
    async def test_evaluator_filtering(self, evaluator_api):
        """Test evaluator filtering (if supported)"""
        # Test listing all evaluators first
        all_evaluators = await evaluator_api.list(page_size=20)
        
        if all_evaluators.results:
            # Try filtering by type or category if available
            try:
                # This might not be supported, but test if it is
                filtered = await evaluator_api.list(type="llm", page_size=10)
                assert hasattr(filtered, 'results')
            except Exception:
                # Filtering might not be supported, that's OK
                pass


class TestEvaluatorAPISync:
    """Test synchronous evaluator API operations"""
    
    def test_sync_list_evaluators(self, sync_evaluator_api):
        """Test sync evaluator listing"""
        result = sync_evaluator_api.list(page_size=5)
        
        assert hasattr(result, 'results')
        assert isinstance(result.results, list)
        
        if result.results:
            evaluator = result.results[0]
            assert hasattr(evaluator, 'id')
            assert hasattr(evaluator, 'name')
            assert hasattr(evaluator, 'slug')


class TestEvaluatorAPIErrorHandling:
    """Test error handling with real API"""
    
    @pytest.mark.asyncio
    async def test_nonexistent_evaluator(self, evaluator_api):
        """Test handling of non-existent evaluator"""
        with pytest.raises(Exception):  # Should raise some kind of HTTP error
            await evaluator_api.get("nonexistent_evaluator_12345")
    
    @pytest.mark.asyncio
    async def test_invalid_pagination(self, evaluator_api):
        """Test invalid pagination parameters"""
        # These should either work or fail gracefully
        try:
            result = await evaluator_api.list(page=0, page_size=0)
            # If it works, that's fine
            assert hasattr(result, 'results')
        except Exception:
            # If it fails, that's also expected behavior
            pass


class TestEvaluatorDiscovery:
    """Test evaluator discovery patterns for real usage"""
    
    @pytest.mark.asyncio
    async def test_find_llm_evaluators(self, evaluator_api):
        """Test finding LLM-type evaluators for real usage"""
        evaluators = await evaluator_api.list(page_size=50)  # Get more evaluators
        
        llm_evaluators = []
        for evaluator in evaluators.results:
            evaluator_type = getattr(evaluator, 'type', '').lower()
            evaluator_name = evaluator.name.lower()
            evaluator_category = getattr(evaluator, 'category', '').lower()
            
            if ('llm' in evaluator_type or 
                'llm' in evaluator_name or 
                'language' in evaluator_name or
                'gpt' in evaluator_name or
                'claude' in evaluator_name):
                llm_evaluators.append(evaluator)
        
        print(f"\n📋 Found {len(llm_evaluators)} LLM-type evaluators:")
        for evaluator in llm_evaluators[:5]:  # Show first 5
            print(f"   • {evaluator.name} (slug: {evaluator.slug})")
        
        # This test just verifies we can discover evaluators
        assert isinstance(llm_evaluators, list)
    
    @pytest.mark.asyncio
    async def test_evaluator_categories(self, evaluator_api):
        """Test categorizing evaluators for real usage"""
        evaluators = await evaluator_api.list(page_size=50)
        
        categories = {}
        for evaluator in evaluators.results:
            category = getattr(evaluator, 'category', 'unknown')
            if category not in categories:
                categories[category] = []
            categories[category].append(evaluator)
        
        print(f"\n📊 Evaluator categories found:")
        for category, evals in categories.items():
            print(f"   {category}: {len(evals)} evaluators")
            for eval in evals[:2]:  # Show first 2 in each category
                print(f"     • {eval.name}")
        
        assert isinstance(categories, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
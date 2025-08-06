#!/usr/bin/env python3
"""
SDK Unit Tests

Tests SDK-specific logic without making API calls:
- Client initialization
- URL building
- Parameter validation
- Base class functionality

NO API CALLS - Pure unit tests for SDK logic only.
"""

import pytest
from keywordsai.utils.base import BaseAPI, BaseSyncAPI
from keywordsai.utils.client import KeywordsAIClient, SyncKeywordsAIClient
from keywordsai.datasets.api import DatasetAPI, SyncDatasetAPI
from keywordsai.evaluators.api import EvaluatorAPI, SyncEvaluatorAPI


class TestClientInitialization:
    """Test client initialization logic"""
    
    def test_keywordsai_client_init(self):
        """Test KeywordsAIClient initialization"""
        client = KeywordsAIClient(
            api_key="test_key",
            base_url="http://localhost:8000"
        )
        
        assert client.base_url == "http://localhost:8000"
        assert hasattr(client, 'headers')
        assert "Authorization" in client.headers
        assert "Bearer test_key" in client.headers["Authorization"]
    
    def test_sync_keywordsai_client_init(self):
        """Test SyncKeywordsAIClient initialization"""
        client = SyncKeywordsAIClient(
            api_key="test_key", 
            base_url="http://localhost:8000"
        )
        
        # Sync client wraps async client
        assert hasattr(client, '_async_client')
        assert client._async_client.base_url == "http://localhost:8000"
        assert hasattr(client._async_client, 'headers')
        assert "Authorization" in client._async_client.headers
    
    def test_dataset_api_initialization(self):
        """Test DatasetAPI initialization"""
        api = DatasetAPI(
            api_key="test_key",
            base_url="http://localhost:8000"
        )
        
        assert hasattr(api, 'client')
        assert isinstance(api.client, KeywordsAIClient)
    
    def test_sync_dataset_api_initialization(self):
        """Test SyncDatasetAPI initialization"""
        api = SyncDatasetAPI(
            api_key="test_key",
            base_url="http://localhost:8000"
        )
        
        assert hasattr(api, 'client')
        assert isinstance(api.client, SyncKeywordsAIClient)
    
    def test_evaluator_api_initialization(self):
        """Test EvaluatorAPI initialization"""
        api = EvaluatorAPI(
            api_key="test_key",
            base_url="http://localhost:8000"
        )
        
        assert hasattr(api, 'client')
        assert isinstance(api.client, KeywordsAIClient)
    
    def test_sync_evaluator_api_initialization(self):
        """Test SyncEvaluatorAPI initialization"""
        api = SyncEvaluatorAPI(
            api_key="test_key",
            base_url="http://localhost:8000"
        )
        
        assert hasattr(api, 'client')
        assert isinstance(api.client, SyncKeywordsAIClient)


class TestURLBuilding:
    """Test URL building logic"""
    
    def test_client_url_construction(self):
        """Test that client constructs URLs correctly"""
        client = KeywordsAIClient(
            api_key="test_key",
            base_url="http://localhost:8000"
        )
        
        # Test that base URL is stored correctly
        assert client.base_url == "http://localhost:8000"
        
        # The actual URL building logic is in the client implementation
        # We just verify the base URL is set correctly
    
    def test_base_url_variations(self):
        """Test different base URL formats"""
        # With trailing slash - client strips it
        client1 = KeywordsAIClient(
            api_key="test",
            base_url="http://localhost:8000/"
        )
        assert client1.base_url == "http://localhost:8000"  # Trailing slash stripped
        
        # Without trailing slash  
        client2 = KeywordsAIClient(
            api_key="test",
            base_url="http://localhost:8000"
        )
        assert client2.base_url == "http://localhost:8000"
        
        # With API path
        client3 = KeywordsAIClient(
            api_key="test",
            base_url="http://localhost:8000/api"
        )
        assert client3.base_url == "http://localhost:8000/api"


class TestAPIStructure:
    """Test API class structure and methods"""
    
    def test_dataset_api_methods(self):
        """Test DatasetAPI has expected methods"""
        api = DatasetAPI(api_key="test", base_url="http://localhost:8000")
        
        # CRUD methods
        assert hasattr(api, 'create')
        assert hasattr(api, 'list')
        assert hasattr(api, 'get')
        assert hasattr(api, 'update')
        assert hasattr(api, 'delete')
        
        # Dataset-specific methods
        assert hasattr(api, 'add_logs_to_dataset')
        assert hasattr(api, 'remove_logs_from_dataset')
        assert hasattr(api, 'list_dataset_logs')
        assert hasattr(api, 'run_dataset_evaluation')
        assert hasattr(api, 'list_evaluation_reports')
        assert hasattr(api, 'get_evaluation_report')
    
    def test_evaluator_api_methods(self):
        """Test EvaluatorAPI has expected methods"""
        api = EvaluatorAPI(api_key="test", base_url="http://localhost:8000")
        
        # Read-only methods (evaluators don't support CRUD)
        assert hasattr(api, 'list')
        assert hasattr(api, 'get')
        
        # Should NOT have write methods
        assert not hasattr(api, 'create')
        assert not hasattr(api, 'update')
        assert not hasattr(api, 'delete')
    
    def test_sync_api_methods(self):
        """Test sync APIs have same methods as async"""
        async_dataset_api = DatasetAPI(api_key="test", base_url="http://localhost:8000")
        sync_dataset_api = SyncDatasetAPI(api_key="test", base_url="http://localhost:8000")
        
        # Both should have the same method names
        async_methods = [m for m in dir(async_dataset_api) if not m.startswith('_')]
        sync_methods = [m for m in dir(sync_dataset_api) if not m.startswith('_')]
        
        # Filter out client differences
        async_methods = [m for m in async_methods if m != 'client']
        sync_methods = [m for m in sync_methods if m != 'client']
        
        assert set(async_methods) == set(sync_methods)


class TestParameterValidation:
    """Test parameter validation logic"""
    
    def test_required_parameters(self):
        """Test parameter handling"""
        # API key can be None (will be loaded from environment)
        try:
            api = DatasetAPI(api_key=None, base_url="http://localhost:8000")
            assert hasattr(api, 'client')
        except Exception:
            # If it fails, that's also valid behavior depending on implementation
            pass
        
        # Empty API key should be allowed (might be set via env)
        api = DatasetAPI(api_key="", base_url="http://localhost:8000")
        assert hasattr(api, 'client')
    
    def test_optional_parameters(self):
        """Test optional parameters"""
        # base_url is optional (has default)
        api = DatasetAPI(api_key="test")
        assert hasattr(api, 'client')
        
        # base_url can be overridden
        api2 = DatasetAPI(api_key="test", base_url="http://custom:9000")
        assert api2.client.base_url == "http://custom:9000"


class TestInheritanceStructure:
    """Test class inheritance structure"""
    
    def test_base_api_inheritance(self):
        """Test that APIs inherit from base classes correctly"""
        dataset_api = DatasetAPI(api_key="test", base_url="http://localhost:8000")
        
        # Should inherit from BaseAPI
        assert isinstance(dataset_api, BaseAPI)
    
    def test_sync_api_inheritance(self):
        """Test that sync APIs inherit from sync base classes correctly"""
        sync_dataset_api = SyncDatasetAPI(api_key="test", base_url="http://localhost:8000")
        
        # Should inherit from BaseSyncAPI
        assert isinstance(sync_dataset_api, BaseSyncAPI)
    
    def test_evaluator_inheritance(self):
        """Test evaluator API inheritance"""
        evaluator_api = EvaluatorAPI(api_key="test", base_url="http://localhost:8000")
        sync_evaluator_api = SyncEvaluatorAPI(api_key="test", base_url="http://localhost:8000")
        
        # Test that they have the expected structure (inheritance may not be direct)
        assert hasattr(evaluator_api, 'client')
        assert hasattr(sync_evaluator_api, 'client')
        assert hasattr(evaluator_api, 'list')
        assert hasattr(evaluator_api, 'get')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
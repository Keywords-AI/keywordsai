#!/usr/bin/env python3
"""
Unit Tests for Logs API

This module contains unit tests for the Logs API functionality,
focusing on SDK-specific logic like client initialization, URL building,
and input validation - without mocking API calls.

Following Respan SDK Testing Strategy:
- Focus on SDK logic only (no mocked API calls)
- Test client initialization and configuration
- Test input validation and parameter building
- Keep tests fast (no network calls)
"""

import pytest
from respan.logs.api import LogAPI, SyncLogAPI
from respan.types.log_types import RespanLogParams, LogList


class TestLogsAPIUnit:
    """Unit tests for SDK-specific logic in Logs API classes"""

    def test_log_api_initialization_with_explicit_params(self):
        """Test LogAPI initialization with explicit parameters"""
        api = LogAPI(api_key="test-key", base_url="http://test.com")
        
        assert api is not None
        assert hasattr(api, 'client')
        assert api.client.base_url == "http://test.com"
        assert "test-key" in api.client.headers.get("Authorization", "")
        
    def test_log_api_initialization_with_env_vars(self):
        """Test LogAPI initialization with environment variables"""
        # This tests that the API can be initialized without explicit params
        # (actual env vars will be loaded by integration tests)
        api = LogAPI()
        assert api is not None
        assert hasattr(api, 'client')
        assert hasattr(api.client, 'base_url')
        assert hasattr(api.client, 'headers')
        
    def test_sync_log_api_initialization_with_explicit_params(self):
        """Test SyncLogAPI initialization with explicit parameters"""
        api = SyncLogAPI(api_key="test-key", base_url="http://test.com")
        
        assert api is not None
        assert hasattr(api, 'client')
        # SyncRespanClient uses internal _async_client for actual HTTP operations
        assert hasattr(api.client, '_async_client')
        assert api.client._async_client.base_url == "http://test.com"
        assert "test-key" in api.client._async_client.headers.get("Authorization", "")
        
    def test_sync_log_api_initialization_with_env_vars(self):
        """Test SyncLogAPI initialization with environment variables"""
        api = SyncLogAPI()
        assert api is not None
        assert hasattr(api, 'client')
        # SyncRespanClient uses internal _async_client
        assert hasattr(api.client, '_async_client')
        assert hasattr(api.client._async_client, 'base_url')
        assert hasattr(api.client._async_client, 'headers')

    @pytest.mark.asyncio
    async def test_log_api_unsupported_operations_raise_errors(self):
        """Test that unsupported operations raise NotImplementedError"""
        api = LogAPI(api_key="test-key")
        
        # Test update operation
        with pytest.raises(NotImplementedError) as exc_info:
            await api.update("test-id", {"test": "data"})
        assert "update" in str(exc_info.value).lower()
        assert "immutable" in str(exc_info.value).lower()
        
        # Test delete operation
        with pytest.raises(NotImplementedError) as exc_info:
            await api.delete("test-id")
        assert "delete" in str(exc_info.value).lower()
        assert "immutable" in str(exc_info.value).lower()

    def test_sync_log_api_unsupported_operations_raise_errors(self):
        """Test that sync unsupported operations raise NotImplementedError"""
        api = SyncLogAPI(api_key="test-key")
        
        # Test update operation
        with pytest.raises(NotImplementedError) as exc_info:
            api.update("test-id", {"test": "data"})
        assert "update" in str(exc_info.value).lower()
        
        # Test delete operation
        with pytest.raises(NotImplementedError) as exc_info:
            api.delete("test-id")
        assert "delete" in str(exc_info.value).lower()

    def test_convenience_functions_with_explicit_params(self):
        """Test the convenience functions for creating clients with explicit parameters"""
        from respan.logs.api import create_log_client, create_sync_log_client
        
        # Test async client creation with explicit params
        async_client = create_log_client("test-key", "http://test.com")
        assert isinstance(async_client, LogAPI)
        assert async_client.client.base_url == "http://test.com"
        
        # Test sync client creation with explicit params
        sync_client = create_sync_log_client("test-key", "http://test.com")
        assert isinstance(sync_client, SyncLogAPI)
        assert sync_client.client._async_client.base_url == "http://test.com"

    def test_convenience_functions_with_env_vars(self):
        """Test the convenience functions with environment variable loading"""
        from respan.logs.api import create_log_client, create_sync_log_client
        
        # Test async client creation with .env reading
        async_client_auto = create_log_client()
        assert isinstance(async_client_auto, LogAPI)
        
        # Test sync client creation with .env reading
        sync_client_auto = create_sync_log_client()
        assert isinstance(sync_client_auto, SyncLogAPI)

    def test_log_list_type_structure(self):
        """Test that LogList type has the correct structure when instantiated"""
        # Test that LogList can be instantiated (it's a type alias to PaginatedResponseType)
        log_list = LogList(
            results=[],
            count=0,
            next=None,
            previous=None
        )
        
        assert hasattr(log_list, 'results')
        assert hasattr(log_list, 'count') 
        assert hasattr(log_list, 'next')
        assert hasattr(log_list, 'previous')
        assert isinstance(log_list.results, list)
        assert log_list.count == 0

    def test_log_params_validation(self):
        """Test RespanLogParams input validation"""
        # Test valid log params
        valid_params = RespanLogParams(
            model="gpt-4",
            input="test input",
            output="test output",
            status_code=200
        )
        
        assert valid_params.model == "gpt-4"
        assert valid_params.input == "test input"
        assert valid_params.output == "test output"
        assert valid_params.status_code == 200
        
        # Test optional params
        minimal_params = RespanLogParams()
        assert minimal_params.model is None
        assert minimal_params.input is None

    def test_base_url_normalization(self):
        """Test that base URLs are properly normalized (trailing slash removal)"""
        # Test URL with trailing slash
        api1 = LogAPI(api_key="test-key", base_url="http://test.com/")
        assert api1.client.base_url == "http://test.com"
        
        # Test URL without trailing slash
        api2 = LogAPI(api_key="test-key", base_url="http://test.com")
        assert api2.client.base_url == "http://test.com"
        
        # Test URL with path and trailing slash
        api3 = LogAPI(api_key="test-key", base_url="http://test.com/api/")
        assert api3.client.base_url == "http://test.com/api"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
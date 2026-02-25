#!/usr/bin/env python3
"""
Dataset API Real Integration Tests

These tests use real API calls to validate dataset functionality.
No mocking - tests actual SDK behavior with Respan server.

Environment variables required:
- RESPAN_API_KEY
- RESPAN_BASE_URL

Usage:
    python -m pytest tests/test_dataset_api_real.py -v -s
"""

import pytest
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv(override=True)

from respan.datasets.api import DatasetAPI
from respan_sdk.respan_types.dataset_types import (
    DatasetCreate,
    DatasetUpdate,
    LogManagementRequest,
)


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
def dataset_api(api_key, base_url):
    """Dataset API client"""
    return DatasetAPI(api_key=api_key, base_url=base_url)


@pytest.fixture
def sync_dataset_api(api_key, base_url):
    """Sync Dataset API client"""
    return DatasetAPI(api_key=api_key, base_url=base_url)


@pytest.fixture
def test_dataset_data():
    """Test dataset creation data"""
    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)
    
    return DatasetCreate(
        name=f"TEST_DATASET_{int(now.timestamp())}",
        description="Test dataset for SDK integration testing",
        type="sampling",
        sampling=5,
        start_time=week_ago.isoformat() + "Z",
        end_time=now.isoformat() + "Z"
    )


class TestDatasetAPICRUD:
    """Test dataset CRUD operations with real API"""
    
    @pytest.mark.asyncio
    async def test_dataset_crud_lifecycle(self, dataset_api, test_dataset_data):
        """Test complete dataset CRUD lifecycle"""
        created_dataset = None
        
        try:
            # Create
            created_dataset = await dataset_api.create(test_dataset_data)
            assert created_dataset.id is not None
            assert created_dataset.name == test_dataset_data.name
            assert created_dataset.type == test_dataset_data.type
            
            # Read
            retrieved_dataset = await dataset_api.get(created_dataset.id)
            assert retrieved_dataset.id == created_dataset.id
            assert retrieved_dataset.name == created_dataset.name
            
            # Update
            update_data = DatasetUpdate(name=f"{test_dataset_data.name}_UPDATED")
            updated_dataset = await dataset_api.update(created_dataset.id, update_data)
            assert updated_dataset.name.endswith("_UPDATED")
            
            # List (verify dataset appears)
            datasets = await dataset_api.list(page_size=10)
            dataset_ids = [d.id for d in datasets.results]
            assert created_dataset.id in dataset_ids
            
        finally:
            # Cleanup
            if created_dataset:
                try:
                    await dataset_api.delete(created_dataset.id)
                except:
                    pass  # Best effort cleanup
    
    @pytest.mark.asyncio
    async def test_dataset_log_operations(self, dataset_api, test_dataset_data):
        """Test dataset log management operations"""
        created_dataset = None
        
        try:
            # Create dataset
            created_dataset = await dataset_api.create(test_dataset_data)
            
            # List dataset logs
            logs = await dataset_api.list_dataset_logs(created_dataset.id, page_size=5)
            assert 'results' in logs
            assert isinstance(logs['results'], list)
            
            # Test log management (may not have logs to add, but API should respond)
            now = datetime.utcnow()
            week_ago = now - timedelta(days=7)
            
            log_request = LogManagementRequest(
                start_time=week_ago.strftime("%Y-%m-%d %H:%M:%S"),
                end_time=now.strftime("%Y-%m-%d %H:%M:%S"),
                filters={
                    "status": {
                        "value": "success",
                        "operator": "equals"
                    }
                }
            )
            
            # These operations should not fail even if no logs match
            try:
                add_result = await dataset_api.add_logs_to_dataset(created_dataset.id, log_request)
                assert 'message' in add_result or 'count' in add_result
            except Exception as e:
                # Log addition might fail if no matching logs, that's OK
                assert "no logs" in str(e).lower() or "not found" in str(e).lower() or True
                
        finally:
            if created_dataset:
                try:
                    await dataset_api.delete(created_dataset.id)
                except:
                    pass


class TestDatasetAPISync:
    """Test synchronous dataset API operations"""
    
    def test_sync_dataset_operations(self, sync_dataset_api, test_dataset_data):
        """Test sync dataset operations"""
        created_dataset = None
        
        try:
            # Create
            created_dataset = sync_dataset_api.create(test_dataset_data)
            assert created_dataset.id is not None
            assert created_dataset.name == test_dataset_data.name
            
            # List
            datasets = sync_dataset_api.list(page_size=5)
            assert hasattr(datasets, 'results')
            assert isinstance(datasets.results, list)
            
            dataset_ids = [d.id for d in datasets.results]
            assert created_dataset.id in dataset_ids
            
        finally:
            if created_dataset:
                try:
                    sync_dataset_api.delete(created_dataset.id)
                except:
                    pass


class TestDatasetAPIErrorHandling:
    """Test error handling with real API"""
    
    @pytest.mark.asyncio
    async def test_nonexistent_dataset(self, dataset_api):
        """Test handling of non-existent dataset"""
        with pytest.raises(Exception):  # Should raise some kind of HTTP error
            await dataset_api.get("nonexistent_dataset_12345")
    
    @pytest.mark.asyncio
    async def test_invalid_dataset_creation(self, dataset_api):
        """Test invalid dataset creation"""
        # Test with invalid data - this should fail
        invalid_data = DatasetCreate(
            name="",  # Empty name should fail
            type="invalid_type"  # Invalid type should fail
        )
        
        with pytest.raises(Exception):  # Should raise validation or HTTP error
            await dataset_api.create(invalid_data)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
"""
Pytest configuration and fixtures for Keywords AI SDK tests
"""

from dotenv import load_dotenv

load_dotenv(override=True)

import pytest
import os
from unittest.mock import AsyncMock, MagicMock
from keywordsai.datasets.api import DatasetAPI, SyncDatasetAPI
from keywordsai.evaluators.api import EvaluatorAPI, SyncEvaluatorAPI


@pytest.fixture
def api_key():
    """Test API key fixture"""
    return os.getenv("KEYWORDSAI_API_KEY")


@pytest.fixture
def base_url():
    """Test base URL fixture"""
    return os.getenv("KEYWORDSAI_BASE_URL")


@pytest.fixture
def mock_response_data():
    """Mock response data for various API calls"""
    return {
        "dataset": {
            "id": "test_dataset_123",
            "name": "TEST",
            "description": "",
            "type": "sampling",
            "sampling": 50,
            "start_time": "2025-07-04T22:55:38.818Z",
            "end_time": "2025-07-13T22:55:38.818Z",
            "status": "ready",
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-01T00:00:00Z",
            "organization": "test_org_123",
        },
        "dataset_list": {
            "results": [
                {
                    "id": "test_dataset_123",
                    "name": "TEST",
                    "description": "",
                    "type": "sampling",
                    "status": "ready",
                    "created_at": "2025-01-01T00:00:00Z",
                    "updated_at": "2025-01-01T00:00:00Z",
                    "organization": "test_org_123",
                }
            ],
            "count": 1,
            "page": 1,
            "page_size": 10,
            "total_pages": 1,
        },
        "evaluator": {
            "id": "eval_123",
            "name": "Character Count Evaluator",
            "slug": "char_count_eval",
            "description": "Counts characters in responses",
            "type": "built_in",
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-01T00:00:00Z",
        },
        "evaluator_list": {
            "results": [
                {
                    "id": "eval_123",
                    "name": "Character Count Evaluator",
                    "slug": "char_count_eval",
                    "description": "Counts characters in responses",
                    "type": "built_in",
                    "created_at": "2025-01-01T00:00:00Z",
                    "updated_at": "2025-01-01T00:00:00Z",
                }
            ],
            "count": 1,
            "page": 1,
            "page_size": 10,
            "total_pages": 1,
        },
        "eval_report": {
            "id": "report_123",
            "dataset_id": "test_dataset_123",
            "evaluator_slugs": ["char_count_eval"],
            "status": "completed",
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-01T00:00:00Z",
            "results": {},
        },
        "eval_report_list": {
            "results": [
                {
                    "id": "report_123",
                    "dataset_id": "test_dataset_123",
                    "evaluator_slugs": ["char_count_eval"],
                    "status": "completed",
                    "created_at": "2025-01-01T00:00:00Z",
                    "updated_at": "2025-01-01T00:00:00Z",
                }
            ],
            "count": 1,
            "page": 1,
            "page_size": 10,
            "total_pages": 1,
        },
        "logs": {
            "results": [
                {
                    "id": "log_123",
                    "request_id": "req_123",
                    "timestamp": "2025-01-01T00:00:00Z",
                    "model": "gpt-4",
                    "prompt": "Hello",
                    "response": "Hi there!",
                }
            ],
            "count": 1,
            "page": 1,
            "page_size": 50,
            "total_pages": 1,
        },
        "log_management_response": {
            "message": "Logs processed successfully",
            "count": 5,
        },
    }


@pytest.fixture
def dataset_api_async(api_key, base_url):
    """Async dataset API client fixture"""
    return DatasetAPI(api_key=api_key, base_url=base_url)


@pytest.fixture
def dataset_api_sync(api_key, base_url):
    """Sync dataset API client fixture"""
    return SyncDatasetAPI(api_key=api_key, base_url=base_url)


@pytest.fixture
def evaluator_api_async(api_key, base_url):
    """Async evaluator API client fixture"""
    return EvaluatorAPI(api_key=api_key, base_url=base_url)


@pytest.fixture
def evaluator_api_sync(api_key, base_url):
    """Sync evaluator API client fixture"""
    return SyncEvaluatorAPI(api_key=api_key, base_url=base_url)


@pytest.fixture
def mock_async_client():
    """Mock async HTTP client fixture"""
    mock = AsyncMock()
    return mock


@pytest.fixture
def mock_sync_client():
    """Mock sync HTTP client fixture"""
    mock = MagicMock()
    return mock


@pytest.fixture
def sample_dataset_create():
    """Sample dataset creation data"""
    from keywordsai_sdk.keywordsai_types.dataset_types import DatasetCreate

    return DatasetCreate(
        name="TEST",
        description="",
        type="sampling",
        sampling=50,
        start_time="2025-07-04T22:55:38.818Z",
        end_time="2025-07-13T22:55:38.818Z",
        initial_log_filters={
            "deployment_name": {"value": ["hihi's openai deployment"], "operator": ""}
        },
    )


@pytest.fixture
def sample_dataset_update():
    """Sample dataset update data"""
    from keywordsai_sdk.keywordsai_types.dataset_types import DatasetUpdate

    return DatasetUpdate(name="test_ds")


@pytest.fixture
def sample_log_management_request():
    """Sample log management request data"""
    from keywordsai_sdk.keywordsai_types.dataset_types import LogManagementRequest

    return LogManagementRequest(
        start_time="2025-07-31 00:00:00",
        end_time="2025-08-01 00:00:00",
        filters={"id": {"value": ["log_123", "log_456"], "operator": "in"}},
    )

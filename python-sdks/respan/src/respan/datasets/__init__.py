"""
Keywords AI Dataset APIs

This module provides functionality for managing datasets, including:
- Creating and managing datasets
- Adding/removing logs from datasets
- Running evaluations on datasets
- Listing and retrieving dataset information
"""

from respan.datasets.api import (
    DatasetAPI,
    create_dataset_client,
)
from respan.types.dataset_types import (
    Dataset,
    DatasetCreate,
    DatasetUpdate,
    DatasetList,
    LogManagementRequest,
    EvalRunRequest,
    EvalReport,
    EvalReportList,
)

# Export main classes and functions
__all__ = [
    "DatasetAPI",
    "create_dataset_client",
    # Re-export types for convenience
    "Dataset",
    "DatasetCreate",
    "DatasetUpdate",
    "DatasetList",
    "LogManagementRequest",
    "EvalRunRequest",
    "EvalReport",
    "EvalReportList",
]

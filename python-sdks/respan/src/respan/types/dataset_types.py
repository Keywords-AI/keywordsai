"""
Dataset Type Definitions for Keywords AI SDK

This module provides comprehensive type definitions for dataset operations in Keywords AI.
All types are Pydantic models that provide validation, serialization, and clear structure
for API interactions.

🏗️ CORE TYPES:

Dataset: Complete dataset information returned by the API
DatasetCreate: Parameters for creating new datasets
DatasetUpdate: Parameters for updating existing datasets
DatasetList: Paginated list of datasets with metadata
LogManagementRequest: Parameters for adding/removing logs from datasets

💡 USAGE PATTERNS:

1. CREATING DATASETS:
   Use DatasetCreate to specify dataset configuration, including time ranges,
   filtering criteria, and sampling parameters.

2. UPDATING DATASETS:
   Use DatasetUpdate to modify dataset metadata like name and description.
   Core properties like type and filters cannot be changed after creation.

3. LOG MANAGEMENT:
   Use LogManagementRequest to add or remove logs based on time ranges and filters.
   Supports complex filtering with various operators.

4. LISTING DATASETS:
   DatasetList provides paginated results with navigation metadata.

📖 EXAMPLES:

Basic dataset creation:
    >>> from respan.types.dataset_types import DatasetCreate
    >>> from datetime import datetime, timedelta
    >>> 
    >>> # Create a sampling dataset for recent logs
    >>> end_time = datetime.utcnow()
    >>> start_time = end_time - timedelta(hours=24)
    >>> 
    >>> dataset_config = DatasetCreate(
    ...     name="Daily Analysis Dataset",
    ...     description="Analysis of API calls from the last 24 hours",
    ...     type="sampling",
    ...     sampling=1000,
    ...     start_time=start_time.isoformat() + "Z",
    ...     end_time=end_time.isoformat() + "Z",
    ...     initial_log_filters={
    ...         "status": {"value": "success", "operator": "equals"}
    ...     }
    ... )

Advanced filtering example:
    >>> # Complex filtering with multiple criteria
    >>> dataset_config = DatasetCreate(
    ...     name="Error Analysis Dataset",
    ...     description="Failed API calls for debugging",
    ...     type="sampling",
    ...     sampling=500,
    ...     start_time="2024-01-01T00:00:00Z",
    ...     end_time="2024-01-02T00:00:00Z",
    ...     initial_log_filters={
    ...         "status": {"value": "error", "operator": "equals"},
    ...         "model": {"value": "gpt-4", "operator": "equals"},
    ...         "response_time": {"value": 5000, "operator": "greater_than"}
    ...     }
    ... )

Log management example:
    >>> from respan.types.dataset_types import LogManagementRequest
    >>> 
    >>> # Add logs with specific criteria
    >>> log_request = LogManagementRequest(
    ...     start_time="2024-01-01 00:00:00",
    ...     end_time="2024-01-01 23:59:59",
    ...     filters={
    ...         "user_id": {"value": "user123", "operator": "equals"},
    ...         "tokens": {"value": 1000, "operator": "less_than"}
    ...     }
    ... )

🔧 FIELD REFERENCE:

DatasetCreate Fields:
- name (str): Human-readable dataset name
- description (str): Detailed description of dataset purpose
- type (str): "sampling" or "llm" - determines collection strategy
- sampling (int, optional): Max number of logs for sampling type
- start_time (str, optional): ISO format timestamp for log collection start
- end_time (str, optional): ISO format timestamp for log collection end
- initial_log_filters (dict, optional): Filters to apply during collection

DatasetUpdate Fields:
- name (str, optional): New dataset name
- description (str, optional): New dataset description

LogManagementRequest Fields:
- start_time (str): Start time in "YYYY-MM-DD HH:MM:SS" format
- end_time (str): End time in "YYYY-MM-DD HH:MM:SS" format
- filters (dict): Filter criteria with operator-based matching

Filter Operators:
- "equals": Exact match
- "not_equals": Exclude exact matches
- "contains": Substring match (for text fields)
- "greater_than": Numeric comparison >
- "less_than": Numeric comparison <
- "greater_than_or_equal": Numeric comparison >=
- "less_than_or_equal": Numeric comparison <=
- "in": Match any value in provided list
- "not_in": Exclude values in provided list

⚠️ IMPORTANT NOTES:
- All datetime strings should be in UTC timezone
- Sampling limits depend on your plan and available logs
- Complex filters may impact dataset creation performance
- Some fields are immutable after dataset creation
"""

# Re-export all dataset types from respan-sdk
from respan_sdk.respan_types.dataset_types import (
    Dataset,
    DatasetCreate,
    DatasetUpdate,
    LogManagementRequest,
    EvalReport,
    EvalRunRequest,
)
from respan.types.generic_types import PaginatedResponseType

# Type alias for log list responses using the generic paginated type
DatasetList = PaginatedResponseType[Dataset]
EvalReportList = PaginatedResponseType[EvalReport]

__all__ = [
    "Dataset",
    "DatasetCreate",
    "DatasetUpdate",
    "DatasetList",
    "LogManagementRequest",
    "EvalReport",
    "EvalReportList",
    "EvalRunRequest",
]
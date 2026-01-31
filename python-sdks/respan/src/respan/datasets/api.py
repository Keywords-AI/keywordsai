"""
Keywords AI Dataset APIs

This module provides functionality for managing datasets, including:
- Creating and managing datasets
- Adding/removing logs from datasets
- Running evaluations on datasets
- Listing and retrieving dataset information
"""

from typing import Optional, Dict, Any, List, Union
from respan_sdk.respan_types.dataset_types import (
    Dataset,
    DatasetCreate,
    DatasetUpdate,
    DatasetList,
    LogManagementRequest,
)
from respan.types.dataset_types import (
    EvalReport,
    EvalReportList,
)
from respan.utils.base import BaseAPI
from respan.constants.dataset_constants import (
    DATASET_BASE_PATH,
    DATASET_CREATION_PATH,
    DATASET_LIST_PATH,
    DATASET_GET_PATH,
    DATASET_UPDATE_PATH,
)


class DatasetAPI(BaseAPI[Dataset, DatasetList, DatasetCreate, DatasetUpdate]):
    """
    Unified Dataset API client for Keywords AI with both sync and async methods.

    This class provides comprehensive functionality for managing datasets in Keywords AI,
    including creating datasets, managing logs within datasets, running evaluations,
    and retrieving results. All operations are available in both synchronous and
    asynchronous variants.

    Features:
        - Create and manage datasets with various filtering options
        - Add/remove logs from datasets based on time ranges and filters
        - Run evaluations on datasets using available evaluators
        - Retrieve evaluation reports and results
        - Full CRUD operations for dataset management

    Args:
        api_key (str): Your Keywords AI API key. Required for authentication.
        base_url (str, optional): Base URL for the Keywords AI API.
            Defaults to the standard Keywords AI API endpoint.

    Example (Synchronous):
        >>> from respan.datasets.api import DatasetAPI
        >>> from respan_sdk.respan_types.dataset_types import DatasetCreate
        >>>
        >>> # Initialize the client
        >>> client = DatasetAPI(api_key="your-api-key")
        >>>
        >>> # Create a new dataset (synchronous - no await)
        >>> dataset_data = DatasetCreate(
        ...     name="My Test Dataset",
        ...     description="Dataset for testing purposes",
        ...     type="sampling",
        ...     sampling=100
        ... )
        >>> dataset = client.create(dataset_data)
        >>> print(f"Created dataset: {dataset.name}")

    Example (Asynchronous):
        >>> import asyncio
        >>> from respan.datasets.api import DatasetAPI
        >>> from respan_sdk.respan_types.dataset_types import DatasetCreate
        >>>
        >>> async def main():
        ...     # Initialize the client
        ...     client = DatasetAPI(api_key="your-api-key")
        ...
        ...     # Create a new dataset (asynchronous - with await)
        ...     dataset_data = DatasetCreate(
        ...         name="My Async Dataset",
        ...         description="Dataset created with async method",
        ...         type="sampling",
        ...         sampling=100
        ...     )
        ...     dataset = await client.acreate(dataset_data)
        ...     print(f"Created dataset: {dataset.name}")
        >>>
        >>> asyncio.run(main())

    Note:
        - Use await client.amethod() for asynchronous operations
        - Use client.method() for synchronous operations
    """

    def __init__(self, api_key: str, base_url: str = None):
        """
        Initialize the Dataset API client.

        Args:
            api_key (str): Your Keywords AI API key for authentication
            base_url (str, optional): Custom base URL for the API. If not provided,
                uses the default Keywords AI API endpoint.
        """
        super().__init__(api_key, base_url)

    # Asynchronous methods (with "a" prefix)
    async def acreate(self, create_data: Union[Dict[str, Any], DatasetCreate]) -> Dataset:
        """
        Create a new dataset with specified parameters (asynchronous).

        This method creates a new dataset in Keywords AI with the provided configuration.
        The dataset can be configured for different types of log collection and filtering.

        Args:
            create_data (Union[Dict[str, Any], DatasetCreate]): Dataset creation parameters including:
                - name (str): Name of the dataset
                - description (str): Description of the dataset's purpose
                - type (str): Dataset type ("sampling" or "llm")
                - sampling (int, optional): Number of logs to sample (for sampling type)
                - start_time (str, optional): Start time for log collection (ISO format)
                - end_time (str, optional): End time for log collection (ISO format)
                - initial_log_filters (dict, optional): Filters to apply when collecting logs

        Returns:
            Dataset: The created dataset object containing:
                - id (str): Unique identifier for the dataset
                - name (str): Dataset name
                - description (str): Dataset description
                - type (str): Dataset type
                - status (str): Current status of the dataset
                - created_at (str): Creation timestamp

        Raises:
            RespanError: If the dataset creation fails due to invalid parameters
                or API errors

        Example:
            >>> from datetime import datetime, timedelta
            >>> from respan_sdk.respan_types.dataset_types import DatasetCreate
            >>>
            >>> # Create a dataset for the last 24 hours with success logs
            >>> end_time = datetime.utcnow()
            >>> start_time = end_time - timedelta(days=1)
            >>>
            >>> dataset_data = DatasetCreate(
            ...     name="Success Logs Analysis",
            ...     description="Dataset containing successful API calls from last 24h",
            ...     type="sampling",
            ...     sampling=500,
            ...     start_time=start_time.isoformat() + "Z",
            ...     end_time=end_time.isoformat() + "Z",
            ...     initial_log_filters={
            ...         "status": {"value": "success", "operator": "equals"}
            ...     }
            ... )
            >>> dataset = await client.acreate(dataset_data)
        """
        # Validate and prepare the input data
        validated_data = self._validate_input(create_data, DatasetCreate)
        
        response = await self.client.post(
            DATASET_CREATION_PATH,
            json_data=self._prepare_json_data(validated_data),
        )
        return Dataset(**response)

    async def alist(
        self, page: Optional[int] = None, page_size: Optional[int] = None, **filters
    ) -> DatasetList:
        """
        List datasets with optional filtering and pagination (asynchronous).

        Retrieve a paginated list of datasets, optionally filtered by various criteria.
        This method supports filtering by dataset properties and provides pagination
        for handling large numbers of datasets.

        Args:
            page (int, optional): Page number for pagination (1-based).
                Defaults to 1 if not specified.
            page_size (int, optional): Number of datasets per page.
                Defaults to API default (usually 20) if not specified.
            **filters: Additional filter parameters such as:
                - name (str): Filter by dataset name (partial match)
                - type (str): Filter by dataset type ("sampling", "llm")
                - status (str): Filter by dataset status
                - created_after (str): Filter datasets created after this date
                - created_before (str): Filter datasets created before this date

        Returns:
            DatasetList: A paginated list containing:
                - results (List[Dataset]): List of dataset objects
                - count (int): Total number of datasets matching filters
                - next (str, optional): URL for next page if available
                - previous (str, optional): URL for previous page if available

        Example:
            >>> # List all datasets
            >>> datasets = await client.alist()
            >>> print(f"Found {datasets.count} datasets")
            >>>
            >>> # List with pagination
            >>> page1 = await client.alist(page=1, page_size=10)
            >>>
            >>> # List with filters
            >>> sampling_datasets = await client.alist(type="sampling")
            >>> recent_datasets = await client.alist(
            ...     created_after="2024-01-01T00:00:00Z"
            ... )
        """
        params = {}
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["page_size"] = page_size
        params.update(filters)

        response = await self.client.get(DATASET_LIST_PATH, params=params)
        return DatasetList(**response)

    async def aget(self, resource_id: str) -> Dataset:
        """
        Retrieve a specific dataset by its unique identifier (asynchronous).

        Fetch detailed information about a dataset including its current status,
        configuration, and metadata. This is useful for checking dataset readiness
        before performing operations like adding logs or running evaluations.

        Args:
            resource_id (str): The unique identifier of the dataset to retrieve.
                This is typically returned when creating a dataset or listing datasets.

        Returns:
            Dataset: Complete dataset information including:
                - id (str): Unique dataset identifier
                - name (str): Dataset name
                - description (str): Dataset description
                - type (str): Dataset type ("sampling" or "llm")
                - status (str): Current status ("initializing", "ready", "running", etc.)
                - created_at (str): Creation timestamp
                - updated_at (str): Last update timestamp
                - log_count (int, optional): Number of logs in the dataset

        Raises:
            RespanError: If the dataset is not found or access is denied

        Example:
            >>> # Get dataset details
            >>> dataset = await client.aget("dataset-123")
            >>> print(f"Dataset '{dataset.name}' status: {dataset.status}")
            >>>
            >>> # Check if dataset is ready for operations
            >>> if dataset.status == "ready":
            ...     print("Dataset is ready for log management and evaluations")
            ... else:
            ...     print(f"Dataset is still {dataset.status}, please wait...")
        """
        response = await self.client.get(f"{DATASET_GET_PATH}/{resource_id}")
        return Dataset(**response)

    async def aupdate(self, resource_id: str, update_data: Union[Dict[str, Any], DatasetUpdate]) -> Dataset:
        """
        Update an existing dataset's properties (asynchronous).

        Modify dataset metadata such as name and description. Note that core
        dataset properties like type and initial filters cannot be changed
        after creation.

        Args:
            resource_id (str): The unique identifier of the dataset to update
            update_data (Union[Dict[str, Any], DatasetUpdate]): Update parameters containing:
                - name (str, optional): New name for the dataset
                - description (str, optional): New description for the dataset

        Returns:
            Dataset: The updated dataset object with new properties applied

        Raises:
            RespanError: If the dataset is not found, update fails, or
                invalid parameters are provided

        Example:
            >>> from respan_sdk.respan_types.dataset_types import DatasetUpdate
            >>>
            >>> # Update dataset name and description
            >>> update_data = DatasetUpdate(
            ...     name="Updated Dataset Name",
            ...     description="Updated description with more details"
            ... )
            >>> updated_dataset = await client.aupdate("dataset-123", update_data)
            >>> print(f"Updated dataset: {updated_dataset.name}")
        """
                # Validate and prepare the input data
        validated_data = self._validate_input(update_data, DatasetUpdate, partial=True)

        response = await self.client.patch(
            f"{DATASET_UPDATE_PATH}/{resource_id}",
            json_data=self._prepare_json_data(validated_data, partial=True),
        )
        return Dataset(**response)

    async def adelete(self, resource_id: str) -> Dict[str, Any]:
        """
        Delete a dataset permanently (asynchronous).

        WARNING: This operation is irreversible. The dataset and all its associated
        logs and evaluation reports will be permanently deleted.

        Args:
            resource_id (str): The unique identifier of the dataset to delete

        Returns:
            Dict[str, Any]: API response confirming deletion, typically containing:
                - message (str): Confirmation message
                - deleted_at (str): Timestamp of deletion

        Raises:
            RespanError: If the dataset is not found or deletion fails

        Example:
            >>> # Delete a dataset (be careful!)
            >>> response = await client.adelete("dataset-123")
            >>> print(response["message"])  # "Dataset deleted successfully"

        Note:
            Consider exporting important data before deletion as this operation
            cannot be undone.
        """
        return await self.client.delete(f"{DATASET_BASE_PATH}/{resource_id}")

    # Synchronous methods (without "a" prefix)
    def create(self, create_data: Union[Dict[str, Any], DatasetCreate]) -> Dataset:
        """Create a new dataset with specified parameters (synchronous)."""
        # Validate and prepare the input data
        validated_data = self._validate_input(create_data, DatasetCreate)
        
        response = self.sync_client.post(
            DATASET_CREATION_PATH,
            json_data=self._prepare_json_data(validated_data),
        )
        return Dataset(**response)

    def list(
        self, page: Optional[int] = None, page_size: Optional[int] = None, **filters
    ) -> DatasetList:
        """List datasets with optional filtering and pagination (synchronous)."""
        params = {}
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["page_size"] = page_size
        params.update(filters)

        response = self.sync_client.get(DATASET_LIST_PATH, params=params)
        return DatasetList(**response)

    def get(self, resource_id: str) -> Dataset:
        """Retrieve a specific dataset by its unique identifier (synchronous)."""
        response = self.sync_client.get(f"{DATASET_GET_PATH}/{resource_id}")
        return Dataset(**response)

    def update(self, resource_id: str, update_data: Union[Dict[str, Any], DatasetUpdate]) -> Dataset:
        """Update an existing dataset's properties (synchronous)."""
                # Validate and prepare the input data
        validated_data = self._validate_input(update_data, DatasetUpdate, partial=True)

        response = self.sync_client.patch(
            f"{DATASET_UPDATE_PATH}/{resource_id}",
            json_data=self._prepare_json_data(validated_data, partial=True),
        )
        return Dataset(**response)

    def delete(self, resource_id: str) -> Dict[str, Any]:
        """Delete a dataset permanently (synchronous)."""
        return self.sync_client.delete(f"{DATASET_BASE_PATH}/{resource_id}")

    # Dataset-specific methods (both sync and async variants)
    async def aadd_logs_to_dataset(
        self, dataset_id: str, log_request: Union[Dict[str, Any], LogManagementRequest]
    ) -> Dict[str, Any]:
        """
        Add logs to an existing dataset based on filters and time range (asynchronous).

        This method allows you to expand a dataset by adding more logs that match
        specific criteria. This is useful for creating comprehensive datasets that
        include different types of logs or extending the time range of analysis.

        Args:
            dataset_id (str): The unique identifier of the target dataset
            log_request (Union[Dict[str, Any], LogManagementRequest]): Log selection criteria containing:
                - start_time (str): Start time for log collection (format: "YYYY-MM-DD HH:MM:SS")
                - end_time (str): End time for log collection (format: "YYYY-MM-DD HH:MM:SS")
                - filters (dict): Log filters such as:
                    - status: {"value": "success|error|pending", "operator": "equals"}
                    - model: {"value": "model-name", "operator": "equals"}
                    - user_id: {"value": "user-123", "operator": "equals"}
                    - Custom filters based on your log structure

        Returns:
            Dict[str, Any]: Response containing:
                - message (str): Success message
                - count (int): Number of logs added
                - dataset_id (str): ID of the updated dataset

        Raises:
            RespanError: If the dataset is not found, request is invalid,
                or no logs match the criteria

        Example:
            >>> from respan_sdk.respan_types.dataset_types import LogManagementRequest
            >>> from datetime import datetime, timedelta
            >>>
            >>> # Add error logs from the last week
            >>> end_time = datetime.utcnow()
            >>> start_time = end_time - timedelta(days=7)
            >>>
            >>> log_request = LogManagementRequest(
            ...     start_time=start_time.strftime("%Y-%m-%d %H:%M:%S"),
            ...     end_time=end_time.strftime("%Y-%m-%d %H:%M:%S"),
            ...     filters={
            ...         "status": {"value": "error", "operator": "equals"}
            ...     }
            ... )
            >>> result = await client.aadd_logs_to_dataset("dataset-123", log_request)
            >>> print(f"Added {result['count']} error logs to dataset")
        """
        # Validate and prepare the input data
        validated_data = self._validate_input(log_request, LogManagementRequest)
        
        return await self.client.post(
            f"{DATASET_BASE_PATH}/{dataset_id}/logs/create",
            json_data=self._prepare_json_data(validated_data),
        )

    def add_logs_to_dataset(
        self, dataset_id: str, log_request: Union[Dict[str, Any], LogManagementRequest]
    ) -> Dict[str, Any]:
        """Add logs to an existing dataset based on filters and time range (synchronous)."""
        # Validate and prepare the input data
        validated_data = self._validate_input(log_request, LogManagementRequest)
        
        return self.sync_client.post(
            f"{DATASET_BASE_PATH}/{dataset_id}/logs/create",
            json_data=self._prepare_json_data(validated_data),
        )

    async def aremove_logs_from_dataset(
        self, dataset_id: str, log_request: Union[Dict[str, Any], LogManagementRequest]
    ) -> Dict[str, Any]:
        """Remove logs from a dataset (asynchronous)"""
        # Validate and prepare the input data
        validated_data = self._validate_input(log_request, LogManagementRequest)
        
        return await self.client.delete(
            f"{DATASET_BASE_PATH}/{dataset_id}/logs/delete",
            json_data=self._prepare_json_data(validated_data),
        )

    def remove_logs_from_dataset(
        self, dataset_id: str, log_request: Union[Dict[str, Any], LogManagementRequest]
    ) -> Dict[str, Any]:
        """Remove logs from a dataset (synchronous)"""
        # Validate and prepare the input data
        validated_data = self._validate_input(log_request, LogManagementRequest)
        
        return self.sync_client.delete(
            f"{DATASET_BASE_PATH}/{dataset_id}/logs/delete",
            json_data=self._prepare_json_data(validated_data),
        )

    async def alist_dataset_logs(
        self,
        dataset_id: str,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        List logs contained within a specific dataset (asynchronous).

        Retrieve a paginated list of all logs currently in the dataset.
        This is useful for inspecting dataset contents, verifying log quality,
        or sampling data for analysis.

        Args:
            dataset_id (str): The unique identifier of the dataset
            page (int, optional): Page number for pagination (1-based).
                Defaults to 1 if not specified.
            page_size (int, optional): Number of logs per page.
                Defaults to API default if not specified.

        Returns:
            Dict[str, Any]: Paginated response containing:
                - results (List[Dict]): List of log objects, each containing:
                    - id (str): Unique log identifier
                    - timestamp (str): When the log was created
                    - status (str): Log status (success, error, etc.)
                    - model (str): Model used for the request
                    - input (str): Input text or prompt
                    - output (str): Generated output
                    - metadata (dict): Additional log metadata
                - count (int): Total number of logs in the dataset
                - next (str, optional): URL for next page
                - previous (str, optional): URL for previous page

        Raises:
            RespanError: If the dataset is not found or access is denied

        Example:
            >>> # List first 10 logs in a dataset
            >>> logs = await client.alist_dataset_logs("dataset-123", page_size=10)
            >>> print(f"Dataset contains {logs['count']} logs")
            >>>
            >>> # Inspect log structure
            >>> for log in logs['results'][:3]:
            ...     print(f"Log {log['id']}: {log['status']} - {log['timestamp']}")
        """
        params = {}
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["page_size"] = page_size

        return await self.client.get(
            f"{DATASET_BASE_PATH}/{dataset_id}/logs", params=params
        )

    def list_dataset_logs(
        self,
        dataset_id: str,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> Dict[str, Any]:
        """List logs contained within a specific dataset (synchronous)."""
        params = {}
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["page_size"] = page_size

        return self.sync_client.get(
            f"{DATASET_BASE_PATH}/{dataset_id}/logs", params=params
        )

    async def arun_dataset_evaluation(
        self, dataset_id: str, evaluator_slugs: List[str], **kwargs
    ) -> Dict[str, Any]:
        """
        Run evaluation on a dataset using specified evaluators (asynchronous).

        Start an evaluation process that will analyze the logs in the dataset
        using the specified evaluators. This is an asynchronous process that
        generates evaluation reports which can be retrieved later.

        Args:
            dataset_id (str): The unique identifier of the dataset to evaluate
            evaluator_slugs (List[str]): List of evaluator slugs to use for evaluation.
                Use the EvaluatorAPI to list available evaluators and their slugs.
            **kwargs: Additional evaluation parameters such as:
                - custom_prompt (str): Custom evaluation prompt
                - evaluation_config (dict): Specific configuration for evaluators

        Returns:
            Dict[str, Any]: Response containing:
                - message (str): Confirmation message
                - evaluation_id (str): Unique identifier for this evaluation run
                - dataset_id (str): ID of the evaluated dataset
                - evaluators (List[str]): List of evaluators being used
                - status (str): Initial status of the evaluation

        Raises:
            RespanError: If the dataset is not found, evaluators are invalid,
                or the evaluation cannot be started

        Example:
            >>> # First, get available evaluators
            >>> from respan.evaluators.api import EvaluatorAPI
            >>> eval_client = EvaluatorAPI(api_key="your-key")
            >>> evaluators = await eval_client.alist()
            >>>
            >>> # Run evaluation with specific evaluators
            >>> result = await client.arun_dataset_evaluation(
            ...     "dataset-123",
            ...     ["accuracy-evaluator", "relevance-evaluator"]
            ... )
            >>> print(f"Started evaluation: {result['evaluation_id']}")

        Note:
            Evaluations run asynchronously. Use `alist_evaluation_reports()` to
            check the status and retrieve results when complete.
        """
        request_data = {"evaluator_slugs": evaluator_slugs, **kwargs}

        return await self.client.post(
            f"{DATASET_BASE_PATH}/{dataset_id}/eval-reports/create",
            json_data=request_data,
        )

    def run_dataset_evaluation(
        self, dataset_id: str, evaluator_slugs: List[str], **kwargs
    ) -> Dict[str, Any]:
        """Run evaluation on a dataset using specified evaluators (synchronous)."""
        request_data = {"evaluator_slugs": evaluator_slugs, **kwargs}

        return self.sync_client.post(
            f"{DATASET_BASE_PATH}/{dataset_id}/eval-reports/create",
            json_data=request_data,
        )

    async def aget_evaluation_report(
        self, dataset_id: str, report_id: str
    ) -> EvalReport:
        """Retrieve a specific evaluation report by ID (asynchronous)"""
        response = await self.client.get(
            f"{DATASET_BASE_PATH}/{dataset_id}/eval-reports/{report_id}"
        )
        return EvalReport(**response)

    def get_evaluation_report(self, dataset_id: str, report_id: str) -> EvalReport:
        """Retrieve a specific evaluation report by ID (synchronous)"""
        response = self.sync_client.get(
            f"{DATASET_BASE_PATH}/{dataset_id}/eval-reports/{report_id}"
        )
        return EvalReport(**response)

    async def alist_evaluation_reports(
        self,
        dataset_id: str,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
        **filters,
    ) -> EvalReportList:
        """List evaluation reports for a dataset (asynchronous)"""
        params = {}
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["page_size"] = page_size
        params.update(filters)

        response = await self.client.get(
            f"{DATASET_BASE_PATH}/{dataset_id}/eval-reports/list/", params=params
        )
        return EvalReportList(**response)

    def list_evaluation_reports(
        self,
        dataset_id: str,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
        **filters,
    ) -> EvalReportList:
        """List evaluation reports for a dataset (synchronous)"""
        params = {}
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["page_size"] = page_size
        params.update(filters)

        response = self.sync_client.get(
            f"{DATASET_BASE_PATH}/{dataset_id}/eval-reports/list/", params=params
        )
        return EvalReportList(**response)


def create_dataset_client(api_key: str, base_url: str = None) -> DatasetAPI:
    """
    Create a unified dataset API client

    Args:
        api_key: Keywords AI API key
        base_url: Base URL for the API (default: KEYWORDS_AI_DEFAULT_BASE_URL)

    Returns:
        DatasetAPI client instance with both sync and async methods
    """
    return DatasetAPI(api_key=api_key, base_url=base_url)


# For backward compatibility, create aliases
SyncDatasetAPI = DatasetAPI  # Same class, just different name for clarity in imports
"""
Keywords AI Logs APIs

This module provides functionality for managing logs, including:
- Creating logs 
- Retrieving individual logs
- Listing logs with filtering and pagination

Note: Logs do not support update or delete operations.
"""

from typing import Optional, Dict, Any
from keywordsai.types.log_types import (
    KeywordsAILogParams,
    KeywordsAIFullLogParams,
    LogList,
)
from keywordsai.utils.client import KeywordsAIClient, SyncKeywordsAIClient
from keywordsai.utils.base import BaseAPI, BaseSyncAPI
from keywordsai.constants.log_constants import (
    LOG_BASE_PATH,
    LOG_CREATION_PATH,
    LOG_LIST_PATH,
    LOG_GET_PATH,
)


class LogAPI(BaseAPI[KeywordsAIFullLogParams, LogList, KeywordsAILogParams, None]):
    """
    Asynchronous Log API client for Keywords AI.

    This class provides functionality for managing logs in Keywords AI,
    including creating logs, retrieving individual logs, and listing logs
    with filtering and pagination.

    Features:
        - Create logs with comprehensive parameters
        - Retrieve individual logs by ID
        - List logs with filtering and pagination
        - Full log details in responses

    Args:
        api_key (str): Your Keywords AI API key. Required for authentication.
        base_url (str, optional): Base URL for the Keywords AI API.
            Defaults to the standard Keywords AI API endpoint.

    Example:
        >>> import asyncio
        >>> from keywordsai.logs.api import LogAPI
        >>> from keywordsai.types.log_types import KeywordsAILogParams
        >>>
        >>> async def main():
        ...     # Initialize the client
        ...     client = LogAPI(api_key="your-api-key")
        ...
        ...     # Create a new log
        ...     log_data = KeywordsAILogParams(
        ...         model="gpt-4",
        ...         input="Hello, world!",
        ...         output="Hi there! How can I help you today?",
        ...         status_code=200
        ...     )
        ...     response = await client.create(log_data)
        ...     print(f"Log created: {response['message']}")
        >>>
        >>> asyncio.run(main())

    Note:
        All methods in this class are asynchronous and should be called with `await`.
        For synchronous operations, use `SyncLogAPI` instead.
        
        Logs do not support update or delete operations - these methods will raise
        NotImplementedError if called.
    """

    def __init__(self, api_key: str = None, base_url: str = None):
        """
        Initialize the Log API client.

        Args:
            api_key (str, optional): Your Keywords AI API key for authentication.
                If not provided, reads from KEYWORDSAI_API_KEY environment variable.
            base_url (str, optional): Custom base URL for the API. If not provided,
                reads from KEYWORDSAI_BASE_URL environment variable or uses default.
        """
        super().__init__(api_key, base_url)

    async def create(self, create_data: KeywordsAILogParams) -> Dict[str, Any]:
        """
        Create a new log with specified parameters.

        This method creates a new log entry in Keywords AI with the provided data.
        The log can include various parameters like model, input/output, status,
        and metadata.

        Args:
            create_data (KeywordsAILogParams): Log creation parameters including:
                - model (str, optional): Model used for the request
                - input (str, optional): Input text or prompt
                - output (str, optional): Generated output
                - status_code (int, optional): HTTP status code
                - error_message (str, optional): Error message if any
                - custom_identifier (str, optional): Custom identifier for grouping
                - And many other optional fields for comprehensive logging

        Returns:
            Dict[str, Any]: Response from the API, typically containing:
                - message (str): Success message like "log successful"
                
        Note:
            The log create endpoint is designed for high throughput and returns
            only a success message, not the full log object. Use the list() or get()
            methods to retrieve detailed log information.

        Raises:
            KeywordsAIError: If the log creation fails due to invalid parameters
                or API errors

        Example:
            >>> from datetime import datetime
            >>> from keywordsai.types.log_types import KeywordsAILogParams
            >>>
            >>> # Create a log for a successful API call
            >>> log_data = KeywordsAILogParams(
            ...     model="gpt-4",
            ...     input="What is the capital of France?",
            ...     output="The capital of France is Paris.",
            ...     status_code=200,
            ...     custom_identifier="geography_qa_001",
            ...     timestamp=datetime.utcnow()
            ... )
            >>> response = await client.create(log_data)
            >>> print(f"Log creation response: {response['message']}")
        """
        response = await self.client.post(
            LOG_CREATION_PATH,
            json_data=create_data.model_dump(exclude_none=True, mode="json"),
        )
        return response

    async def list(
        self, page: Optional[int] = None, page_size: Optional[int] = None, **filters
    ) -> LogList:
        """
        List logs with optional filtering and pagination.

        Retrieve a paginated list of logs, optionally filtered by various criteria.
        This method supports filtering by log properties and provides pagination
        for handling large numbers of logs.

        Args:
            page (int, optional): Page number for pagination (1-based).
                Defaults to 1 if not specified.
            page_size (int, optional): Number of logs per page.
                Defaults to API default (usually 20) if not specified.
            **filters: Additional filter parameters such as:
                - model (str): Filter by model name
                - status (str): Filter by log status
                - user_id (str): Filter by user ID
                - start_time (str): Filter logs after this timestamp (ISO format)
                - end_time (str): Filter logs before this timestamp (ISO format)
                - custom_identifier (str): Filter by custom identifier
                - error_bit (int): Filter by error status (0=success, 1=error)

        Returns:
            LogList: A paginated list containing:
                - results (List[KeywordsAIFullLogParams]): List of log objects
                - count (int): Total number of logs matching filters
                - next (str, optional): URL for next page if available
                - previous (str, optional): URL for previous page if available

        Example:
            >>> # List all logs
            >>> logs = await client.list()
            >>> print(f"Found {logs.count} logs")
            >>>
            >>> # List with pagination
            >>> page1 = await client.list(page=1, page_size=10)
            >>>
            >>> # List with filters
            >>> error_logs = await client.list(error_bit=1)
            >>> recent_logs = await client.list(
            ...     start_time="2024-01-01T00:00:00Z",
            ...     model="gpt-4"
            ... )
        """
        params = {}
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["page_size"] = page_size
        params.update(filters)

        response = await self.client.get(LOG_LIST_PATH, params=params)
        return LogList(**response)

    async def get(self, resource_id: str) -> KeywordsAIFullLogParams:
        """
        Retrieve a specific log by its unique identifier.

        Fetch detailed information about a log including all its parameters
        and metadata. This is useful for inspecting individual logs or
        retrieving logs for analysis.

        Args:
            resource_id (str): The unique identifier of the log to retrieve.
                This can be either the 'id' or 'unique_id' field from the log.

        Returns:
            KeywordsAIFullLogParams: Complete log information including:
                - All user-provided parameters (input, output, model, etc.)
                - System-generated metadata (timestamps, IDs, etc.)
                - Authentication information (user_id, organization_id, etc.)
                - Status and error information
                - Usage statistics and performance metrics

        Raises:
            KeywordsAIError: If the log is not found or access is denied

        Example:
            >>> # Get log details
            >>> log = await client.get("log-123")
            >>> print(f"Log '{log.id}' - Model: {log.model}")
            >>> print(f"Input: {log.input}")
            >>> print(f"Output: {log.output}")
            >>> print(f"Status: {log.status_code}")
        """
        response = await self.client.get(f"{LOG_GET_PATH}/{resource_id}")
        return KeywordsAIFullLogParams(**response)

    async def update(self, resource_id: str, update_data) -> KeywordsAIFullLogParams:
        """
        Update operation is not supported for logs.

        Args:
            resource_id (str): The log ID (ignored)
            update_data: Update data (ignored)

        Raises:
            NotImplementedError: Always raised as logs cannot be updated
        """
        raise NotImplementedError(
            "Logs do not support update operations. Logs are immutable once created."
        )

    async def delete(self, resource_id: str) -> Dict[str, Any]:
        """
        Delete operation is not supported for logs.

        Args:
            resource_id (str): The log ID (ignored)

        Raises:
            NotImplementedError: Always raised as logs cannot be deleted
        """
        raise NotImplementedError(
            "Logs do not support delete operations. Logs are immutable for audit purposes."
        )


class SyncLogAPI(BaseSyncAPI[KeywordsAIFullLogParams, LogList, KeywordsAILogParams, None]):
    """
    Synchronous Log API client for Keywords AI.

    This class provides the same functionality as LogAPI but with synchronous
    method calls. Use this when you prefer traditional blocking calls or when
    working in environments where async/await is not suitable.

    All methods in this class are direct synchronous equivalents of the async
    methods in LogAPI. See LogAPI documentation for detailed method
    descriptions and examples.

    Args:
        api_key (str): Your Keywords AI API key. Required for authentication.
        base_url (str, optional): Base URL for the Keywords AI API.

    Example:
        >>> from keywordsai.logs.api import SyncLogAPI
        >>> from keywordsai.types.log_types import KeywordsAILogParams
        >>>
        >>> # Initialize synchronous client
        >>> client = SyncLogAPI(api_key="your-api-key")
        >>>
        >>> # Create log (no await needed)
        >>> log_data = KeywordsAILogParams(
        ...     model="gpt-4",
        ...     input="Hello",
        ...     output="Hi there!",
        ...     status_code=200
        ... )
        >>> response = client.create(log_data)
        >>> print(f"Log created: {response['message']}")

    Note:
        For new projects, consider using the async LogAPI as it provides
        better performance and scalability for I/O operations.
        
        Logs do not support update or delete operations - these methods will raise
        NotImplementedError if called.
    """

    def __init__(self, api_key: str = None, base_url: str = None):
        """
        Initialize the synchronous Log API client.

        Args:
            api_key (str, optional): Your Keywords AI API key for authentication.
                If not provided, reads from KEYWORDSAI_API_KEY environment variable.
            base_url (str, optional): Custom base URL for the API. If not provided,
                reads from KEYWORDSAI_BASE_URL environment variable or uses default.
        """
        super().__init__(api_key, base_url)

    def create(self, create_data: KeywordsAILogParams) -> Dict[str, Any]:
        """Create a new log (synchronous)"""
        response = self.client.post(
            LOG_CREATION_PATH,
            json_data=create_data.model_dump(exclude_none=True, mode="json"),
        )
        return response

    def list(
        self, page: Optional[int] = None, page_size: Optional[int] = None, **filters
    ) -> LogList:
        """List logs with optional filtering (synchronous)"""
        params = {}
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["page_size"] = page_size
        params.update(filters)

        response = self.client.get(LOG_LIST_PATH, params=params)
        return LogList(**response)

    def get(self, resource_id: str) -> KeywordsAIFullLogParams:
        """Retrieve a specific log by ID (synchronous)"""
        response = self.client.get(f"{LOG_GET_PATH}/{resource_id}")
        return KeywordsAIFullLogParams(**response)

    def update(self, resource_id: str, update_data) -> KeywordsAIFullLogParams:
        """
        Update operation is not supported for logs.

        Args:
            resource_id (str): The log ID (ignored)
            update_data: Update data (ignored)

        Raises:
            NotImplementedError: Always raised as logs cannot be updated
        """
        raise NotImplementedError(
            "Logs do not support update operations. Logs are immutable once created."
        )

    def delete(self, resource_id: str) -> Dict[str, Any]:
        """
        Delete operation is not supported for logs.

        Args:
            resource_id (str): The log ID (ignored)

        Raises:
            NotImplementedError: Always raised as logs cannot be deleted
        """
        raise NotImplementedError(
            "Logs do not support delete operations. Logs are immutable for audit purposes."
        )


# Convenience functions for creating clients
def create_log_client(api_key: str = None, base_url: str = None) -> LogAPI:
    """
    Create an async log API client

    Args:
        api_key: Keywords AI API key (optional, reads from KEYWORDSAI_API_KEY env var if not provided)
        base_url: Base URL for the API (optional, reads from KEYWORDSAI_BASE_URL env var or uses default)

    Returns:
        LogAPI client instance
    """
    return LogAPI(api_key=api_key, base_url=base_url)


def create_sync_log_client(api_key: str = None, base_url: str = None) -> SyncLogAPI:
    """
    Create a synchronous log API client

    Args:
        api_key: Keywords AI API key (optional, reads from KEYWORDSAI_API_KEY env var if not provided)
        base_url: Base URL for the API (optional, reads from KEYWORDSAI_BASE_URL env var or uses default)

    Returns:
        SyncLogAPI client instance
    """
    return SyncLogAPI(api_key=api_key, base_url=base_url)
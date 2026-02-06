"""
Keywords AI Evaluator APIs

This module provides functionality for managing evaluators, including:
- Listing available evaluators
- Getting evaluator details
- Running evaluations
- Managing evaluation reports
"""

from typing import Optional, Dict, Any
from respan.types.evaluator_types import (
    Evaluator,
    EvaluatorList,
)
from respan.utils.base import BaseAPI
from respan.constants.evaluator_constants import (
    EVALUATOR_BASE_PATH,
    EVALUATOR_LIST_PATH,
    EVALUATOR_GET_PATH,
)


class EvaluatorAPI(BaseAPI[Evaluator, EvaluatorList, None, None]):
    """
    Unified Evaluator API client for Keywords AI with both sync and async methods.
    
    This class provides functionality for discovering and working with evaluators
    in Keywords AI. Evaluators are pre-built or custom tools that analyze and
    score your AI model outputs based on various criteria such as accuracy,
    relevance, toxicity, and more.
    
    Features:
        - List available evaluators with filtering and pagination
        - Get detailed information about specific evaluators
        - Discover evaluator capabilities and configuration options
    
    Args:
        api_key (str): Your Keywords AI API key. Required for authentication.
        base_url (str, optional): Base URL for the Keywords AI API.
            Defaults to the standard Keywords AI API endpoint.
    
    Example (Synchronous):
        >>> from respan.evaluators.api import EvaluatorAPI
        >>> 
        >>> # Initialize the client
        >>> client = EvaluatorAPI(api_key="your-api-key")
        >>> 
        >>> # List all available evaluators (synchronous)
        >>> evaluators = client.list()
        >>> print(f"Found {evaluators.count} evaluators")
        >>> 
        >>> # Get details of a specific evaluator
        >>> evaluator = client.get("accuracy-evaluator")
        >>> print(f"Evaluator: {evaluator.name}")
    
    Example (Asynchronous):
        >>> import asyncio
        >>> from respan.evaluators.api import EvaluatorAPI
        >>> 
        >>> async def main():
        ...     # Initialize the client
        ...     client = EvaluatorAPI(api_key="your-api-key")
        ...     
        ...     # List all available evaluators (asynchronous)
        ...     evaluators = await client.alist()
        ...     print(f"Found {evaluators.count} evaluators")
        ...     
        ...     # Get details of a specific evaluator
        ...     evaluator = await client.aget("accuracy-evaluator")
        ...     print(f"Evaluator: {evaluator.name}")
        >>> 
        >>> asyncio.run(main())
    
    Note:
        - Use await client.amethod() for asynchronous operations
        - Use client.method() for synchronous operations
        
        Evaluators are read-only resources. You cannot create, update, or delete
        evaluators through this API. Use the web interface to manage custom evaluators.
    """
    
    def __init__(self, api_key: str, base_url: str = None):
        """
        Initialize the Evaluator API client.
        
        Args:
            api_key (str): Your Keywords AI API key for authentication
            base_url (str, optional): Custom base URL for the API. If not provided,
                uses the default Keywords AI API endpoint.
        """
        super().__init__(api_key, base_url)
    
    # Asynchronous methods (with "a" prefix)
    async def alist(
        self,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
        **filters
    ) -> EvaluatorList:
        """
        List available evaluators with optional filtering and pagination (asynchronous).
        
        Retrieve a paginated list of evaluators available in your Keywords AI
        account. This includes both built-in evaluators and any custom evaluators
        you've created.

        Args:
            page (int, optional): Page number for pagination (1-based).
                Defaults to 1 if not specified.
            page_size (int, optional): Number of evaluators per page.
                Defaults to API default (usually 20) if not specified.
            **filters: Additional filter parameters such as:
                - category (str): Filter by evaluator category
                - name (str): Filter by evaluator name (partial match)
                - type (str): Filter by evaluator type ("built-in", "custom")

        Returns:
            EvaluatorList: A paginated list containing:
                - results (List[Evaluator]): List of evaluator objects
                - count (int): Total number of evaluators matching filters
                - next (str, optional): URL for next page if available
                - previous (str, optional): URL for previous page if available

        Example:
            >>> # List all evaluators
            >>> evaluators = await client.alist()
            >>> print(f"Found {evaluators.count} evaluators")
            >>> 
            >>> # List with pagination
            >>> page1 = await client.alist(page=1, page_size=5)
            >>> 
            >>> # List with filters
            >>> accuracy_evaluators = await client.alist(category="accuracy")
            >>> custom_evaluators = await client.alist(type="custom")
        """
        params = {}
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["page_size"] = page_size
        params.update(filters)

        response = await self.client.get(EVALUATOR_LIST_PATH, params=params)
        return EvaluatorList(**response)

    async def aget(self, resource_id: str) -> Evaluator:
        """
        Retrieve detailed information about a specific evaluator (asynchronous).

        Fetch complete information about an evaluator, including its configuration,
        capabilities, supported parameters, and usage examples.

        Args:
            resource_id (str): The unique identifier or slug of the evaluator to retrieve.
                This can be either the evaluator's ID or its human-readable slug.

        Returns:
            Evaluator: Complete evaluator information including:
                - id (str): Unique evaluator identifier
                - slug (str): Human-readable evaluator slug
                - name (str): Display name of the evaluator
                - description (str): Detailed description of what the evaluator does
                - category (str): Category the evaluator belongs to
                - type (str): Type of evaluator ("built-in" or "custom")
                - parameters (dict): Configuration parameters the evaluator accepts
                - examples (list): Usage examples and expected outputs

        Raises:
            RespanError: If the evaluator is not found or access is denied

        Example:
            >>> # Get evaluator by slug (recommended)
            >>> evaluator = await client.aget("accuracy-evaluator")
            >>> print(f"Evaluator: {evaluator.name}")
            >>> print(f"Description: {evaluator.description}")
            >>> print(f"Category: {evaluator.category}")
            >>> 
            >>> # Get evaluator by ID
            >>> evaluator = await client.aget("eval-123")
        """
        response = await self.client.get(f"{EVALUATOR_GET_PATH}/{resource_id}")
        return Evaluator(**response)

    async def acreate(self, create_data) -> Evaluator:
        """
        Create operation is not supported for evaluators (asynchronous).

        Args:
            create_data: Create data (ignored)

        Raises:
            NotImplementedError: Always raised as evaluators cannot be created via API
        """
        raise NotImplementedError(
            "Evaluators cannot be created through the API. Use the Keywords AI web interface to create custom evaluators."
        )

    async def aupdate(self, resource_id: str, update_data) -> Evaluator:
        """
        Update operation is not supported for evaluators (asynchronous).

        Args:
            resource_id (str): The evaluator ID (ignored)
            update_data: Update data (ignored)

        Raises:
            NotImplementedError: Always raised as evaluators cannot be updated via API
        """
        raise NotImplementedError(
            "Evaluators cannot be updated through the API. Use the Keywords AI web interface to modify custom evaluators."
        )

    async def adelete(self, resource_id: str) -> Dict[str, Any]:
        """
        Delete operation is not supported for evaluators (asynchronous).

        Args:
            resource_id (str): The evaluator ID (ignored)

        Raises:
            NotImplementedError: Always raised as evaluators cannot be deleted via API
        """
        raise NotImplementedError(
            "Evaluators cannot be deleted through the API. Use the Keywords AI web interface to delete custom evaluators."
        )

    # Synchronous methods (without "a" prefix)
    def list(
        self,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
        **filters
    ) -> EvaluatorList:
        """
        List available evaluators with optional filtering and pagination (synchronous).
        """
        params = {}
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["page_size"] = page_size
        params.update(filters)

        response = self.sync_client.get(EVALUATOR_LIST_PATH, params=params)
        return EvaluatorList(**response)
    
    def get(self, resource_id: str) -> Evaluator:
        """
        Retrieve detailed information about a specific evaluator (synchronous).

        Args:
            resource_id (str): The unique identifier or slug of the evaluator to retrieve

        Returns:
            Evaluator: Complete evaluator information

        Example:
            >>> # Get evaluator by slug (recommended)
            >>> evaluator = client.get("accuracy-evaluator")
            >>> print(f"Evaluator: {evaluator.name}")
            >>> print(f"Description: {evaluator.description}")
            >>> print(f"Category: {evaluator.category}")
        """
        response = self.sync_client.get(f"{EVALUATOR_GET_PATH}/{resource_id}")
        return Evaluator(**response)

    def create(self, create_data) -> Evaluator:
        """
        Create operation is not supported for evaluators (synchronous).

        Args:
            create_data: Create data (ignored)

        Raises:
            NotImplementedError: Always raised as evaluators cannot be created via API
        """
        raise NotImplementedError(
            "Evaluators cannot be created through the API. Use the Keywords AI web interface to create custom evaluators."
        )

    def update(self, resource_id: str, update_data) -> Evaluator:
        """
        Update operation is not supported for evaluators (synchronous).

        Args:
            resource_id (str): The evaluator ID (ignored)
            update_data: Update data (ignored)

        Raises:
            NotImplementedError: Always raised as evaluators cannot be updated via API
        """
        raise NotImplementedError(
            "Evaluators cannot be updated through the API. Use the Keywords AI web interface to modify custom evaluators."
        )

    def delete(self, resource_id: str) -> Dict[str, Any]:
        """
        Delete operation is not supported for evaluators (synchronous).

        Args:
            resource_id (str): The evaluator ID (ignored)

        Raises:
            NotImplementedError: Always raised as evaluators cannot be deleted via API
        """
        raise NotImplementedError(
            "Evaluators cannot be deleted through the API. Use the Keywords AI web interface to delete custom evaluators."
        )


def create_evaluator_client(api_key: str, base_url: str = None) -> EvaluatorAPI:
    """
    Create a unified evaluator API client
    
    Args:
        api_key: Keywords AI API key
        base_url: Base URL for the API (default: KEYWORDS_AI_DEFAULT_BASE_URL)
        
    Returns:
        EvaluatorAPI client instance with both sync and async methods
    """
    return EvaluatorAPI(api_key=api_key, base_url=base_url)


# For backward compatibility, create aliases
SyncEvaluatorAPI = EvaluatorAPI  # Same class, just different name for clarity in imports
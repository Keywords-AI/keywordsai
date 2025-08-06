"""
Keywords AI Evaluator APIs

This module provides functionality for managing evaluators, including:
- Listing available evaluators
- Getting evaluator details
- Running evaluations
- Managing evaluation reports
"""

from typing import Optional, Dict, Any
from keywordsai.types.evaluator_types import (
    Evaluator,
    EvaluatorList,
)
from keywordsai.utils.client import KeywordsAIClient, SyncKeywordsAIClient
from keywordsai.utils.base import BaseAPI, BaseSyncAPI
from keywordsai.constants.evaluator_constants import (
    EVALUATOR_BASE_PATH,
    EVALUATOR_LIST_PATH,
    EVALUATOR_GET_PATH,
)


# Since evaluators don't have Create/Update/Delete operations, we'll create a simpler base
class EvaluatorAPI:
    """
    Asynchronous Evaluator API client for Keywords AI.
    
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
    
    Example:
        >>> import asyncio
        >>> from keywordsai.evaluators.api import EvaluatorAPI
        >>> 
        >>> async def main():
        ...     # Initialize the client
        ...     client = EvaluatorAPI(api_key="your-api-key")
        ...     
        ...     # List all available evaluators
        ...     evaluators = await client.list()
        ...     print(f"Found {len(evaluators.results)} evaluators")
        ...     
        ...     # Find LLM-based evaluators
        ...     llm_evaluators = await client.list(category="llm")
        ...     for eval in llm_evaluators.results:
        ...         print(f"- {eval.name}: {eval.description}")
        >>> 
        >>> asyncio.run(main())
    
    Note:
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
        self.client = KeywordsAIClient(api_key=api_key, base_url=base_url)
    
    async def list(
        self,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
        **filters
    ) -> EvaluatorList:
        """
        List available evaluators with optional filtering and pagination.
        
        Retrieve a paginated list of evaluators available in your Keywords AI
        account. This includes both built-in evaluators and any custom evaluators
        you've created.

        Args:
            page (int, optional): Page number for pagination (1-based).
                Defaults to 1 if not specified.
            page_size (int, optional): Number of evaluators per page.
                Defaults to API default (usually 20) if not specified.
            **filters: Additional filter parameters such as:
                - name (str): Filter by evaluator name (partial match)
                - category (str): Filter by category ("llm", "rule_based", "ml")
                - type (str): Filter by type ("accuracy", "relevance", "toxicity", etc.)
                - is_active (bool): Filter by active status

        Returns:
            EvaluatorList: A paginated list containing:
                - results (List[Evaluator]): List of evaluator objects, each containing:
                    - id (str): Unique evaluator identifier
                    - name (str): Human-readable evaluator name
                    - slug (str): URL-safe identifier used in API calls
                    - description (str): Detailed description of what the evaluator does
                    - category (str): Evaluator category
                    - type (str): Specific evaluation type
                    - is_active (bool): Whether the evaluator is currently available
                    - configuration (dict): Evaluator-specific settings
                - count (int): Total number of evaluators matching filters
                - next (str, optional): URL for next page if available
                - previous (str, optional): URL for previous page if available
                
        Example:
            >>> # List all evaluators
            >>> evaluators = await client.list()
            >>> print(f"Available evaluators: {evaluators.count}")
            >>> 
            >>> # List LLM-based evaluators only
            >>> llm_evals = await client.list(category="llm")
            >>> for evaluator in llm_evals.results:
            ...     print(f"- {evaluator.name} (slug: {evaluator.slug})")
            >>> 
            >>> # Paginated listing
            >>> page1 = await client.list(page=1, page_size=5)
        """
        params = {}
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["page_size"] = page_size
        params.update(filters)
        
        response = await self.client.get(EVALUATOR_LIST_PATH, params=params)
        return EvaluatorList(**response)
    
    async def get(self, resource_id: str) -> Evaluator:
        """
        Retrieve detailed information about a specific evaluator.
        
        Get comprehensive details about an evaluator including its configuration,
        capabilities, and usage instructions. This is useful for understanding
        what an evaluator does before using it in dataset evaluations.

        Args:
            resource_id (str): The unique identifier or slug of the evaluator to retrieve.
                This can be either the evaluator's ID or its slug (URL-safe name).

        Returns:
            Evaluator: Complete evaluator information including:
                - id (str): Unique evaluator identifier
                - name (str): Human-readable evaluator name
                - slug (str): URL-safe identifier for API usage
                - description (str): Detailed description of the evaluator's purpose
                - category (str): Evaluator category ("llm", "rule_based", "ml")
                - type (str): Specific evaluation type ("accuracy", "relevance", etc.)
                - is_active (bool): Whether the evaluator is currently available
                - configuration (dict): Evaluator-specific configuration options
                - input_schema (dict): Expected input format
                - output_schema (dict): Expected output format
                - created_at (str): Creation timestamp
                - updated_at (str): Last update timestamp
                
        Raises:
            KeywordsAIError: If the evaluator is not found or access is denied
            
        Example:
            >>> # Get evaluator by slug (recommended)
            >>> evaluator = await client.get("accuracy-evaluator")
            >>> print(f"Evaluator: {evaluator.name}")
            >>> print(f"Description: {evaluator.description}")
            >>> print(f"Category: {evaluator.category}")
            >>> 
            >>> # Check if evaluator is available
            >>> if evaluator.is_active:
            ...     print("Evaluator is ready to use")
            ... else:
            ...     print("Evaluator is currently unavailable")
            
        Note:
            Use the slug (not the ID) when calling run_dataset_evaluation()
            in the DatasetAPI.
        """
        response = await self.client.get(f"{EVALUATOR_GET_PATH}/{resource_id}")
        return Evaluator(**response)
    



class SyncEvaluatorAPI:
    """
    Synchronous Evaluator API client for Keywords AI.
    
    This class provides the same functionality as EvaluatorAPI but with synchronous
    method calls. Use this when you prefer traditional blocking calls or when
    working in environments where async/await is not suitable.
    
    All methods in this class are direct synchronous equivalents of the async
    methods in EvaluatorAPI. See EvaluatorAPI documentation for detailed method
    descriptions and examples.
    
    Args:
        api_key (str): Your Keywords AI API key. Required for authentication.
        base_url (str, optional): Base URL for the Keywords AI API.
    
    Example:
        >>> from keywordsai.evaluators.api import SyncEvaluatorAPI
        >>> 
        >>> # Initialize synchronous client
        >>> client = SyncEvaluatorAPI(api_key="your-api-key")
        >>> 
        >>> # List evaluators (no await needed)
        >>> evaluators = client.list()
        >>> print(f"Found {len(evaluators.results)} evaluators")
        >>> 
        >>> # Get specific evaluator
        >>> accuracy_eval = client.get("accuracy-evaluator")
        >>> print(f"Evaluator: {accuracy_eval.name}")
    
    Note:
        For new projects, consider using the async EvaluatorAPI as it provides
        better performance and scalability for I/O operations.
    """
    
    def __init__(self, api_key: str, base_url: str = None):
        """
        Initialize the synchronous Evaluator API client.
        
        Args:
            api_key (str): Your Keywords AI API key for authentication
            base_url (str, optional): Custom base URL for the API
        """
        self.client = SyncKeywordsAIClient(api_key=api_key, base_url=base_url)
    
    def list(
        self,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
        **filters
    ) -> EvaluatorList:
        """List available evaluators (synchronous)"""
        params = {}
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["page_size"] = page_size
        params.update(filters)
        
        response = self.client.get(EVALUATOR_LIST_PATH, params=params)
        return EvaluatorList(**response)
    
    def get(self, resource_id: str) -> Evaluator:
        """Retrieve a specific evaluator by ID (synchronous)"""
        response = self.client.get(f"{EVALUATOR_GET_PATH}/{resource_id}")
        return Evaluator(**response)
    



# Convenience functions for creating clients
def create_evaluator_client(api_key: str, base_url: str = None) -> EvaluatorAPI:
    """
    Create an async evaluator API client
    
    Args:
        api_key: Keywords AI API key
        base_url: Base URL for the API (default: KEYWORDS_AI_DEFAULT_BASE_URL)
        
    Returns:
        EvaluatorAPI client instance
    """
    return EvaluatorAPI(api_key=api_key, base_url=base_url)


def create_sync_evaluator_client(api_key: str, base_url: str = None) -> SyncEvaluatorAPI:
    """
    Create a synchronous evaluator API client
    
    Args:
        api_key: Keywords AI API key
        base_url: Base URL for the API (default: KEYWORDS_AI_DEFAULT_BASE_URL)
        
    Returns:
        SyncEvaluatorAPI client instance
    """
    return SyncEvaluatorAPI(api_key=api_key, base_url=base_url)

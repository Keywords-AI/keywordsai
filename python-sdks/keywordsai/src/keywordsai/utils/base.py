"""
Abstract base classes for Keywords AI API clients

This module provides abstract base classes that define common CRUDL (Create, Read, Update, Delete, List)
operations for API clients, ensuring consistent interfaces across different resource types.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, TypeVar, Generic
from keywordsai.utils.client import KeywordsAIClient, SyncKeywordsAIClient

# Generic type variables for flexibility
T = TypeVar('T')  # For individual resource types
TList = TypeVar('TList')  # For list response types
TCreate = TypeVar('TCreate')  # For create request types
TUpdate = TypeVar('TUpdate')  # For update request types


class BaseAPI(ABC, Generic[T, TList, TCreate, TUpdate]):
    """Abstract base class for async API clients with CRUDL operations"""
    
    def __init__(self, api_key: str, base_url: str = None):
        self.client = KeywordsAIClient(api_key=api_key, base_url=base_url)
    
    @abstractmethod
    async def create(self, create_data: TCreate) -> T:
        """
        Create a new resource
        
        Args:
            create_data: Resource creation parameters
            
        Returns:
            Created resource information
        """
        pass
    
    @abstractmethod
    async def list(
        self, 
        page: Optional[int] = None, 
        page_size: Optional[int] = None, 
        **filters
    ) -> TList:
        """
        List resources with optional filtering and pagination
        
        Args:
            page: Page number for pagination
            page_size: Number of items per page
            **filters: Additional filter parameters
            
        Returns:
            List of resources with pagination info
        """
        pass
    
    @abstractmethod
    async def get(self, resource_id: str) -> T:
        """
        Retrieve a specific resource by ID
        
        Args:
            resource_id: ID of the resource to retrieve
            
        Returns:
            Resource information
        """
        pass
    
    @abstractmethod
    async def update(self, resource_id: str, update_data: TUpdate) -> T:
        """
        Update a resource
        
        Args:
            resource_id: ID of the resource to update
            update_data: Resource update parameters
            
        Returns:
            Updated resource information
        """
        pass
    
    @abstractmethod
    async def delete(self, resource_id: str) -> Dict[str, Any]:
        """
        Delete a resource
        
        Args:
            resource_id: ID of the resource to delete
            
        Returns:
            Response from the API
        """
        pass


class BaseSyncAPI(ABC, Generic[T, TList, TCreate, TUpdate]):
    """Abstract base class for synchronous API clients with CRUDL operations"""
    
    def __init__(self, api_key: str, base_url: str = None):
        self.client = SyncKeywordsAIClient(api_key=api_key, base_url=base_url)
    
    @abstractmethod
    def create(self, create_data: TCreate) -> T:
        """
        Create a new resource (synchronous)
        
        Args:
            create_data: Resource creation parameters
            
        Returns:
            Created resource information
        """
        pass
    
    @abstractmethod
    def list(
        self, 
        page: Optional[int] = None, 
        page_size: Optional[int] = None, 
        **filters
    ) -> TList:
        """
        List resources with optional filtering and pagination (synchronous)
        
        Args:
            page: Page number for pagination
            page_size: Number of items per page
            **filters: Additional filter parameters
            
        Returns:
            List of resources with pagination info
        """
        pass
    
    @abstractmethod
    def get(self, resource_id: str) -> T:
        """
        Retrieve a specific resource by ID (synchronous)
        
        Args:
            resource_id: ID of the resource to retrieve
            
        Returns:
            Resource information
        """
        pass
    
    @abstractmethod
    def update(self, resource_id: str, update_data: TUpdate) -> T:
        """
        Update a resource (synchronous)
        
        Args:
            resource_id: ID of the resource to update
            update_data: Resource update parameters
            
        Returns:
            Updated resource information
        """
        pass
    
    @abstractmethod
    def delete(self, resource_id: str) -> Dict[str, Any]:
        """
        Delete a resource (synchronous)
        
        Args:
            resource_id: ID of the resource to delete
            
        Returns:
            Response from the API
        """
        pass

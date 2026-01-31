"""
Abstract base classes for Keywords AI API clients

This module provides abstract base classes that define common CRUDL (Create, Read, Update, Delete, List)
operations for API clients with unified sync/async methods, ensuring consistent interfaces across different resource types.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, TypeVar, Generic, Union
from respan.utils.client import RespanClient, SyncRespanClient
from pydantic import BaseModel

# Generic type variables for flexibility
T = TypeVar('T')  # For individual resource types
TList = TypeVar('TList')  # For list response types
TCreate = TypeVar('TCreate')  # For create request types
TUpdate = TypeVar('TUpdate')  # For update request types


class BaseAPI(ABC, Generic[T, TList, TCreate, TUpdate]):
    """
    Abstract base class for unified sync/async API clients with CRUDL operations.
    
    This class provides the same method names for both synchronous and asynchronous operations.
    The methods automatically detect the calling context and use the appropriate client.
    """
    
    def __init__(self, api_key: str, base_url: str = None):
        self.async_client = RespanClient(api_key=api_key, base_url=base_url)
        self.sync_client = SyncRespanClient(api_key=api_key, base_url=base_url)
        # For backward compatibility with async methods that use self.client
        self.client = self.async_client
    
    def _validate_input(self, data: Union[Dict[str, Any], BaseModel], model_class: type, partial: bool = False) -> BaseModel:
        """
        Validate and convert input data to Pydantic model.
        
        Args:
            data: Either a dictionary or a Pydantic model instance
            model_class: The Pydantic model class to validate against
            partial: If True, only validate provided fields for partial updates
            
        Returns:
            Validated Pydantic model instance
            
        Raises:
            ValueError: If the data is invalid or cannot be converted
        """
        if isinstance(data, dict):
            try:
                if partial:
                    # For partial updates, only create model with provided fields
                    # This prevents default values from being set for unspecified fields
                    return model_class.model_validate(data)
                else:
                    # For full validation, use standard constructor
                    return model_class(**data)
            except Exception as e:
                raise ValueError(f"Invalid data for {model_class.__name__}: {str(e)}")
        elif isinstance(data, BaseModel):
            # If it's already a Pydantic model, validate it's the correct type
            if not isinstance(data, model_class):
                # Try to convert if it's a different Pydantic model
                try:
                    if partial:
                        # For partial updates, only include fields that were explicitly set
                        dump_data = data.model_dump(exclude_unset=True)
                        return model_class.model_validate(dump_data)
                    else:
                        return model_class(**data.model_dump())
                except Exception as e:
                    raise ValueError(f"Cannot convert {type(data).__name__} to {model_class.__name__}: {str(e)}")
            return data
        else:
            raise ValueError(f"Data must be a dictionary or {model_class.__name__} instance, got {type(data)}")
    
    def _prepare_json_data(self, data: Union[Dict[str, Any], BaseModel], partial: bool = False) -> Dict[str, Any]:
        """
        Prepare data for JSON serialization.
        
        Args:
            data: Either a dictionary or a Pydantic model instance
            partial: If True, only include fields that were explicitly set (for partial updates)
            
        Returns:
            Dictionary ready for JSON serialization
        """
        if isinstance(data, BaseModel):
            if partial:
                # For partial updates, exclude unset fields to prevent overriding with defaults
                return data.model_dump(exclude_unset=True, mode="json")
            else:
                # For full operations, exclude None values as before
                return data.model_dump(exclude_none=True, mode="json")
        elif isinstance(data, dict):
            return data
        else:
            raise ValueError(f"Data must be a dictionary or Pydantic model, got {type(data)}")
    
    # Unified methods that work in both sync and async contexts
    @abstractmethod
    async def acreate(self, create_data: Union[Dict[str, Any], TCreate]) -> T:
        """
        Create a new resource (async version)
        
        Args:
            create_data: Resource creation parameters (dict or Pydantic model)
            
        Returns:
            Created resource information
        """
        pass
    
    @abstractmethod
    async def alist(
        self, 
        page: Optional[int] = None, 
        page_size: Optional[int] = None, 
        **filters
    ) -> TList:
        """
        List resources with optional filtering and pagination (async version)
        
        Args:
            page: Page number for pagination
            page_size: Number of items per page
            **filters: Additional filter parameters
            
        Returns:
            List of resources with pagination info
        """
        pass
    
    @abstractmethod
    async def aget(self, resource_id: str) -> T:
        """
        Retrieve a specific resource by ID (async version)
        
        Args:
            resource_id: ID of the resource to retrieve
            
        Returns:
            Resource information
        """
        pass
    
    @abstractmethod
    async def aupdate(self, resource_id: str, update_data: Union[Dict[str, Any], TUpdate]) -> T:
        """
        Update a resource (async version)
        
        Args:
            resource_id: ID of the resource to update
            update_data: Resource update parameters (dict or Pydantic model)
            
        Returns:
            Updated resource information
        """
        pass
    
    @abstractmethod
    async def adelete(self, resource_id: str) -> Dict[str, Any]:
        """
        Delete a resource (async version)
        
        Args:
            resource_id: ID of the resource to delete
            
        Returns:
            Response from the API
        """
        pass

    @abstractmethod
    def create(self, create_data: Union[Dict[str, Any], TCreate]) -> T:
        """
        Create a new resource (synchronous version)
        """
        pass
    
    @abstractmethod
    def list(self, page: Optional[int] = None, page_size: Optional[int] = None, **filters) -> TList:
        """
        List resources with optional filtering and pagination (synchronous version)
        """
        pass
    
    @abstractmethod
    def get(self, resource_id: str) -> T:
        """
        Retrieve a specific resource by ID (synchronous version)
        """
        pass

    @abstractmethod
    def update(self, resource_id: str, update_data: Union[Dict[str, Any], TUpdate]) -> T:
        """
        Update a resource (synchronous version)
        """
        pass
    
    @abstractmethod
    def delete(self, resource_id: str) -> Dict[str, Any]:
        """
        Delete a resource (synchronous version)
        """
        pass
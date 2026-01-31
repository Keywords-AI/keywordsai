"""
Centralized HTTP Client for Keywords AI

This module provides a centralized HTTP client for making API requests to Keywords AI services.
It handles authentication, common headers, and provides both async and sync interfaces.
"""

import httpx
import asyncio
from functools import wraps
from typing import Optional, Dict, Any, Union
from respan.constants import BASE_URL_SUFFIX, KEYWORDS_AI_DEFAULT_BASE_URL
import os


class RespanClient:
    """Centralized async HTTP client for Keywords AI API"""

    def __init__(self, api_key: str = None, base_url: str = None):
        """
        Initialize the Keywords AI client

        Args:
            api_key: Keywords AI API key
            base_url: Base URL for the API KEYWORDS_AI_DEFAULT_BASE_URL
        """
        if not base_url:
            base_url = os.getenv("KEYWORDS_AI_BASE_URL", KEYWORDS_AI_DEFAULT_BASE_URL)
        if not api_key:
            api_key = os.getenv("RESPAN_API_KEY")
        base_url = base_url.rstrip("/")
        if base_url.endswith(BASE_URL_SUFFIX):
            base_url = base_url[: -len(BASE_URL_SUFFIX)]
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Make a GET request

        Args:
            endpoint: API endpoint (without base URL)
            params: Query parameters
            headers: Additional headers

        Returns:
            Response JSON data
        """
        request_headers = self.headers.copy()
        if headers:
            request_headers.update(headers)

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/{endpoint.lstrip('/')}",
                params=params,
                headers=request_headers,
            )
            response.raise_for_status()
            return response.json()

    async def post(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Make a POST request

        Args:
            endpoint: API endpoint (without base URL)
            json_data: JSON data to send
            headers: Additional headers

        Returns:
            Response JSON data
        """
        request_headers = self.headers.copy()
        if headers:
            request_headers.update(headers)

        # Configure timeout properly for httpx
        timeout_config = httpx.Timeout(timeout) if timeout else None

        async with httpx.AsyncClient(timeout=timeout_config) as client:
            response = await client.post(
                f"{self.base_url}/{endpoint.lstrip('/')}",
                json=json_data,
                headers=request_headers,
            )
            response.raise_for_status()
            return response.json()

    async def patch(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Make a PATCH request

        Args:
            endpoint: API endpoint (without base URL)
            json_data: JSON data to send
            headers: Additional headers

        Returns:
            Response JSON data
        """
        request_headers = self.headers.copy()
        if headers:
            request_headers.update(headers)

        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{self.base_url}/{endpoint.lstrip('/')}",
                json=json_data,
                headers=request_headers,
            )
            response.raise_for_status()
            return response.json()

    async def delete(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Make a DELETE request

        Args:
            endpoint: API endpoint (without base URL)
            json_data: JSON data to send
            headers: Additional headers
            timeout: Timeout in seconds

        Returns:
            Response JSON data
        """
        request_headers = self.headers.copy()
        if headers:
            request_headers.update(headers)

        # Configure timeout properly for httpx
        timeout_config = httpx.Timeout(timeout) if timeout else None

        async with httpx.AsyncClient(timeout=timeout_config) as client:
            response = await client.delete(
                f"{self.base_url}/{endpoint.lstrip('/')}",
                json=json_data,
                headers=request_headers,
            )
            response.raise_for_status()
            return response.json()


def sync_wrapper(async_func):
    """Decorator to convert async functions to sync"""

    @wraps(async_func)
    def wrapper(*args, **kwargs):
        return asyncio.run(async_func(*args, **kwargs))

    return wrapper


class SyncRespanClient:
    """Synchronous wrapper around RespanClient"""

    def __init__(self, api_key: str, base_url: str = None):
        """
        Initialize the synchronous Keywords AI client

        Args:
            api_key: Keywords AI API key
            base_url: Base URL for the API (default: None)
        """
        if not base_url:
            base_url = os.getenv("KEYWORDS_AI_BASE_URL", KEYWORDS_AI_DEFAULT_BASE_URL)
        self._async_client = RespanClient(api_key=api_key, base_url=base_url)

    @sync_wrapper
    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make a synchronous GET request"""
        return await self._async_client.get(endpoint, params, headers)

    @sync_wrapper
    async def post(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make a synchronous POST request"""
        return await self._async_client.post(endpoint, json_data, headers)

    @sync_wrapper
    async def patch(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make a synchronous PATCH request"""
        return await self._async_client.patch(endpoint, json_data, headers)

    @sync_wrapper
    async def delete(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make a synchronous DELETE request"""
        return await self._async_client.delete(endpoint, json_data, headers)


# Convenience functions for creating clients
def create_client(api_key: str, base_url: str = None) -> RespanClient:
    """
    Create an async Keywords AI client

    Args:
        api_key: Keywords AI API key
        base_url: Base URL for the API (default: KEYWORDS_AI_DEFAULT_BASE_URL)

    Returns:
        RespanClient instance
    """
    return RespanClient(api_key=api_key, base_url=base_url)


def create_sync_client(api_key: str, base_url: str = None) -> SyncRespanClient:
    """
    Create a synchronous Keywords AI client

    Args:
        api_key: Keywords AI API key
        base_url: Base URL for the API (default: KEYWORDS_AI_DEFAULT_BASE_URL)

    Returns:
        SyncRespanClient instance
    """
    return SyncRespanClient(api_key=api_key, base_url=base_url)


__all__ = [
    "RespanClient",
    "SyncRespanClient",
    "create_client",
    "create_sync_client",
]

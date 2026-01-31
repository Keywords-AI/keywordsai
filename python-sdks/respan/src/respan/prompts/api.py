"""
Keywords AI Prompt APIs

This module provides functionality for managing prompts and prompt versions, including:
- Creating and managing prompts
- Creating and managing prompt versions
- Listing and retrieving prompt information
- Updating prompt configurations
"""

from typing import Optional, Dict, Any, List, Union
from respan_sdk.respan_types.prompt_types import (
    Prompt,
    PromptVersion,
)
from respan.types.prompt_types import (
    PromptCreateResponse,
    PromptListResponse,
    PromptRetrieveResponse,
    PromptVersionCreateResponse,
    PromptVersionListResponse,
    PromptVersionRetrieveResponse,
)
from respan.utils.base import BaseAPI
from respan.constants.prompt_constants import (
    PROMPT_CREATION_PATH,
    PROMPT_LIST_PATH,
    PROMPT_GET_PATH,
    PROMPT_UPDATE_PATH,
    PROMPT_DELETE_PATH,
    PROMPT_VERSION_CREATION_PATH,
    PROMPT_VERSION_LIST_PATH,
    PROMPT_VERSION_GET_PATH,
    PROMPT_VERSION_UPDATE_PATH,
)


class PromptAPI(BaseAPI[PromptRetrieveResponse, PromptListResponse, Prompt, Prompt]):
    """
    Unified Prompt API client for Keywords AI with both sync and async methods.

    This class provides comprehensive functionality for managing prompts and prompt versions
    in Keywords AI, including creating prompts, managing versions with different configurations,
    and retrieving prompt information. All operations are available in both synchronous and
    asynchronous variants.

    Features:
        - Create and manage prompts with metadata
        - Create and manage prompt versions with specific configurations
        - Full CRUD operations for prompt management
        - Version-specific operations for prompt versions
        - Support for prompt templates and variables

    Args:
        api_key (str): Your Keywords AI API key. Required for authentication.
        base_url (str, optional): Base URL for the Keywords AI API.
            Defaults to the standard Keywords AI API endpoint.

    Example (Synchronous):
        >>> from respan.prompts.api import PromptAPI
        >>> from respan_sdk.respan_types.prompt_types import Prompt
        >>>
        >>> # Initialize the client
        >>> client = PromptAPI(api_key="your-api-key")
        >>>
        >>> # Create a new prompt (synchronous - no await)
        >>> prompt_data = Prompt(
        ...     name="Customer Support Assistant",
        ...     description="AI assistant for customer support",
        ...     prompt_id="cust-support-001"
        ... )
        >>> prompt = client.create(prompt_data)
        >>> print(f"Created prompt: {prompt.name}")

    Example (Asynchronous):
        >>> import asyncio
        >>> from respan.prompts.api import PromptAPI
        >>> from respan_sdk.respan_types.prompt_types import Prompt
        >>>
        >>> async def main():
        ...     # Initialize the client
        ...     client = PromptAPI(api_key="your-api-key")
        ...
        ...     # Create a new prompt (asynchronous - with await)
        ...     prompt_data = Prompt(
        ...         name="Async Support Assistant",
        ...         description="AI assistant created with async method",
        ...         prompt_id="async-support-001"
        ...     )
        ...     prompt = await client.acreate(prompt_data)
        ...     print(f"Created prompt: {prompt.name}")
        >>>
        >>> asyncio.run(main())

    Note:
        - Use await client.amethod() for asynchronous operations
        - Use client.method() for synchronous operations
    """

    def __init__(self, api_key: str, base_url: str = None):
        """
        Initialize the Prompt API client.

        Args:
            api_key (str): Your Keywords AI API key for authentication
            base_url (str, optional): Custom base URL for the API. If not provided,
                uses the default Keywords AI API endpoint.
        """
        super().__init__(api_key, base_url)

    # Asynchronous methods (with "a" prefix)
    async def acreate(
        self, create_data: Union[Dict[str, Any], Prompt] = None
    ) -> PromptCreateResponse:
        """
        Create a new prompt with specified parameters (asynchronous).

        This method creates a new prompt in Keywords AI with the provided configuration.
        The prompt serves as a container for multiple versions with different configurations.

        Args:
            create_data (Union[Dict[str, Any], Prompt]): Prompt creation parameters including:
                - name (str, optional): Name of the prompt (defaults to "Untitled")
                - description (str, optional): Description of the prompt's purpose
                - prompt_id (str): Unique identifier for the prompt
                - prompt_slug (str, optional): URL-friendly slug

        Returns:
            PromptCreateResponse: The created prompt object containing:
                - id (str): Unique identifier for the prompt
                - name (str): Prompt name
                - description (str): Prompt description
                - prompt_id (str): Unique prompt identifier
                - created_at (str): Creation timestamp

        Raises:
            RespanError: If the prompt creation fails due to invalid parameters
                or API errors

        Example:
            >>> from respan_sdk.respan_types.prompt_types import Prompt
            >>>
            >>> # Create a basic prompt
            >>> prompt_data = Prompt(
            ...     name="Customer Support Bot",
            ...     description="AI assistant for handling customer inquiries",
            ...     prompt_id="customer-support-v1"
            ... )
            >>> prompt = await client.acreate(prompt_data)
        """
        # For prompt creation, we send a POST request without any data (based on Postman)
        response = await self.client.post(PROMPT_CREATION_PATH)
        return PromptCreateResponse(**response)

    async def alist(
        self, page: Optional[int] = None, page_size: Optional[int] = None, **filters
    ) -> PromptListResponse:
        """
        List prompts with optional filtering and pagination (asynchronous).

        Retrieve a paginated list of prompts, optionally filtered by various criteria.
        This method supports filtering by prompt properties and provides pagination
        for handling large numbers of prompts.

        Args:
            page (int, optional): Page number for pagination (1-based).
                Defaults to 1 if not specified.
            page_size (int, optional): Number of prompts per page.
                Defaults to API default (usually 20) if not specified.
            **filters: Additional filter parameters such as:
                - name (str): Filter by prompt name (partial match)
                - starred (bool): Filter by starred status
                - created_after (str): Filter prompts created after this date
                - created_before (str): Filter prompts created before this date

        Returns:
            PromptListResponse: A paginated list containing:
                - results (List[Prompt]): List of prompt objects
                - count (int): Total number of prompts matching filters
                - next (str, optional): URL for next page if available
                - previous (str, optional): URL for previous page if available

        Example:
            >>> # List all prompts
            >>> prompts = await client.alist()
            >>> print(f"Found {prompts.count} prompts")
            >>>
            >>> # List with pagination
            >>> page1 = await client.alist(page=1, page_size=10)
            >>>
            >>> # List with filters
            >>> starred_prompts = await client.alist(starred=True)
        """
        params = {}
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["page_size"] = page_size
        params.update(filters)

        response = await self.client.get(PROMPT_LIST_PATH, params=params)
        return PromptListResponse(**response)

    async def aget(self, resource_id: str) -> PromptRetrieveResponse:
        """
        Retrieve a specific prompt by its unique identifier (asynchronous).

        Fetch detailed information about a prompt including its current version,
        live version, and metadata. This is useful for getting complete prompt
        information before performing operations like creating versions.

        Args:
            resource_id (str): The unique identifier of the prompt to retrieve.
                This is typically returned when creating a prompt or listing prompts.

        Returns:
            PromptRetrieveResponse: Complete prompt information including:
                - id (str): Unique prompt identifier
                - name (str): Prompt name
                - description (str): Prompt description
                - prompt_id (str): Unique prompt identifier
                - current_version (PromptVersion, optional): Current active version
                - live_version (PromptVersion, optional): Live/published version
                - prompt_versions (List[PromptVersion], optional): All versions
                - commit_count (int): Number of versions
                - starred (bool): Whether prompt is starred
                - tags (List[Dict]): Associated tags

        Raises:
            RespanError: If the prompt is not found or access is denied

        Example:
            >>> # Get prompt details
            >>> prompt = await client.aget("prompt-123")
            >>> print(f"Prompt '{prompt.name}' has {prompt.commit_count} versions")
            >>>
            >>> # Check current version
            >>> if prompt.current_version:
            ...     print(f"Current version: {prompt.current_version.version}")
        """
        response = await self.client.get(f"{PROMPT_GET_PATH}/{resource_id}")
        return PromptRetrieveResponse(**response)

    async def aupdate(
        self, resource_id: str, update_data: Union[Dict[str, Any], Prompt]
    ) -> PromptRetrieveResponse:
        """
        Update an existing prompt's properties (asynchronous).

        Modify prompt metadata such as name and description. Note that core
        prompt properties like prompt_id cannot be changed after creation.

        Args:
            resource_id (str): The unique identifier of the prompt to update
            update_data (Union[Dict[str, Any], Prompt]): Update parameters containing:
                - name (str, optional): New name for the prompt
                - description (str, optional): New description for the prompt

        Returns:
            PromptRetrieveResponse: The updated prompt object with new properties applied

        Raises:
            RespanError: If the prompt is not found, update fails, or
                invalid parameters are provided

        Example:
            >>> from respan_sdk.respan_types.prompt_types import Prompt
            >>>
            >>> # Update prompt name and description
            >>> update_data = Prompt(
            ...     name="Updated Customer Support Bot",
            ...     description="Enhanced AI assistant with improved capabilities"
            ... )
            >>> updated_prompt = await client.aupdate("prompt-123", update_data)
            >>> print(f"Updated prompt: {updated_prompt.name}")
        """
        # Validate and prepare the input data
        validated_data = self._validate_input(update_data, Prompt, partial=True)

        response = await self.client.patch(
            f"{PROMPT_UPDATE_PATH}/{resource_id}",
            json_data=self._prepare_json_data(validated_data, partial=True),
        )
        return PromptRetrieveResponse(**response)

    async def adelete(self, resource_id: str) -> Dict[str, Any]:
        """
        Delete a prompt permanently (asynchronous).

        WARNING: This operation is irreversible. The prompt and all its versions
        will be permanently deleted.

        Args:
            resource_id (str): The unique identifier of the prompt to delete

        Returns:
            Dict[str, Any]: API response confirming deletion, typically containing:
                - message (str): Confirmation message
                - deleted_at (str): Timestamp of deletion

        Raises:
            RespanError: If the prompt is not found or deletion fails

        Example:
            >>> # Delete a prompt (be careful!)
            >>> response = await client.adelete("prompt-123")
            >>> print(response.get("message", "Prompt deleted"))

        Note:
            Consider exporting important prompt data before deletion as this operation
            cannot be undone.
        """
        return await self.client.delete(f"{PROMPT_DELETE_PATH}/{resource_id}")

    # Synchronous methods (without "a" prefix)
    def create(
        self, create_data: Union[Dict[str, Any], Prompt] = None
    ) -> PromptCreateResponse:
        """Create a new prompt with specified parameters (synchronous)."""
        # For prompt creation, we send a POST request without any data (based on Postman)
        response = self.sync_client.post(PROMPT_CREATION_PATH)
        return PromptCreateResponse(**response)

    def list(
        self, page: Optional[int] = None, page_size: Optional[int] = None, **filters
    ) -> PromptListResponse:
        """List prompts with optional filtering and pagination (synchronous)."""
        params = {}
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["page_size"] = page_size
        params.update(filters)

        response = self.sync_client.get(PROMPT_LIST_PATH, params=params)
        return PromptListResponse(**response)

    def get(self, resource_id: str) -> PromptRetrieveResponse:
        """Retrieve a specific prompt by its unique identifier (synchronous)."""
        response = self.sync_client.get(f"{PROMPT_GET_PATH}/{resource_id}")
        return PromptRetrieveResponse(**response)

    def update(
        self, resource_id: str, update_data: Union[Dict[str, Any], Prompt]
    ) -> PromptRetrieveResponse:
        """Update an existing prompt's properties (synchronous)."""
        # Validate and prepare the input data
        validated_data = self._validate_input(update_data, Prompt, partial=True)

        response = self.sync_client.patch(
            f"{PROMPT_UPDATE_PATH}/{resource_id}",
            json_data=self._prepare_json_data(validated_data, partial=True),
        )
        return PromptRetrieveResponse(**response)

    def delete(self, resource_id: str) -> Dict[str, Any]:
        """Delete a prompt permanently (synchronous)."""
        return self.sync_client.delete(f"{PROMPT_DELETE_PATH}/{resource_id}")

    # Deploy methods (both sync and async variants)
    async def adeploy(self, resource_id: str) -> PromptRetrieveResponse:
        """
        Deploy a prompt by setting its live version (asynchronous).

        This method deploys a prompt by sending an update request with deploy=True.
        This triggers the deployment of the most recent readonly version as the live version.

        Args:
            resource_id (str): The unique identifier of the prompt to deploy

        Returns:
            PromptRetrieveResponse: The updated prompt object with deployment status

        Raises:
            RespanError: If the prompt is not found, deployment fails, or
                no readonly version is available for deployment

        Example:
            >>> # Deploy a prompt
            >>> deployed_prompt = await client.adeploy("prompt-123")
            >>> print(f"Deployed prompt: {deployed_prompt.name}")
            >>> print(f"Live version: {deployed_prompt.live_version}")

        Note:
            The prompt must have at least one readonly (committed) version to be deployable.
            Draft versions cannot be deployed directly.
        """
        # Create update data with deploy flag
        deploy_data = {"deploy": True}

        response = await self.client.patch(
            f"{PROMPT_UPDATE_PATH}/{resource_id}",
            json_data=deploy_data,
        )
        return PromptRetrieveResponse(**response)

    def deploy(self, resource_id: str) -> PromptRetrieveResponse:
        """
        Deploy a prompt by setting its live version (synchronous).

        This method deploys a prompt by sending an update request with deploy=True.
        This triggers the deployment of the most recent readonly version as the live version.

        Args:
            resource_id (str): The unique identifier of the prompt to deploy

        Returns:
            PromptRetrieveResponse: The updated prompt object with deployment status

        Raises:
            RespanError: If the prompt is not found, deployment fails, or
                no readonly version is available for deployment

        Example:
            >>> # Deploy a prompt
            >>> deployed_prompt = client.deploy("prompt-123")
            >>> print(f"Deployed prompt: {deployed_prompt.name}")
            >>> print(f"Live version: {deployed_prompt.live_version}")

        Note:
            The prompt must have at least one readonly (committed) version to be deployable.
            Draft versions cannot be deployed directly.
        """
        # Create update data with deploy flag
        deploy_data = {"deploy": True}

        response = self.sync_client.patch(
            f"{PROMPT_UPDATE_PATH}/{resource_id}",
            json_data=deploy_data,
        )
        return PromptRetrieveResponse(**response)

    # Prompt version-specific methods (both sync and async variants)
    async def acreate_version(
        self, prompt_id: str, version_data: Union[Dict[str, Any], PromptVersion]
    ) -> PromptVersionCreateResponse:
        """
        Create a new version for an existing prompt (asynchronous).

        This method creates a new version of a prompt with specific configuration,
        messages, and model parameters. Each version represents a different
        configuration of the same prompt.

        Args:
            prompt_id (str): The unique identifier of the parent prompt
            version_data (Union[Dict[str, Any], PromptVersion]): Version creation parameters including:
                - messages (List[Message]): Conversation messages for the prompt
                - model (str, optional): AI model to use (defaults to "gpt-3.5-turbo")
                - temperature (float, optional): Model temperature (defaults to 0.7)
                - max_tokens (int, optional): Maximum tokens (defaults to 4096)
                - description (str, optional): Version description
                - variables (Dict, optional): Template variables
                - tools (List[Dict], optional): Available tools
                - And other model parameters...

        Returns:
            PromptVersionCreateResponse: The created version object containing:
                - id (str): Unique version identifier
                - prompt_version_id (str): Unique version identifier
                - version (int): Version number
                - messages (List[Message]): Configured messages
                - model (str): Selected AI model
                - All other configuration parameters

        Raises:
            RespanError: If the prompt is not found, version creation fails,
                or invalid parameters are provided

        Example:
            >>> from respan_sdk.respan_types.prompt_types import PromptVersion
            >>> from datetime import datetime
            >>>
            >>> # Create a prompt version with specific configuration
            >>> version_data = PromptVersion(
            ...     prompt_version_id="version-001",
            ...     description="Initial customer support version",
            ...     created_at=datetime.utcnow(),
            ...     updated_at=datetime.utcnow(),
            ...     version=1,
            ...     messages=[
            ...         {"role": "system", "content": "You are a helpful customer support assistant."},
            ...         {"role": "user", "content": "How can I help you today?"}
            ...     ],
            ...     model="gpt-4o-mini",
            ...     temperature=0.7,
            ...     max_tokens=2048,
            ...     parent_prompt="prompt-123"
            ... )
            >>> version = await client.acreate_version("prompt-123", version_data)
            >>> print(f"Created version {version.version}")
        """
        # Validate and prepare the input data
        validated_data = self._validate_input(version_data, PromptVersion)

        response = await self.client.post(
            PROMPT_VERSION_CREATION_PATH(prompt_id),
            json_data=self._prepare_json_data(validated_data),
        )
        return PromptVersionCreateResponse(**response)

    def create_version(
        self, prompt_id: str, version_data: Union[Dict[str, Any], PromptVersion]
    ) -> PromptVersionCreateResponse:
        """Create a new version for an existing prompt (synchronous)."""
        # Validate and prepare the input data
        validated_data = self._validate_input(version_data, PromptVersion)

        response = self.sync_client.post(
            PROMPT_VERSION_CREATION_PATH(prompt_id),
            json_data=self._prepare_json_data(validated_data),
        )
        return PromptVersionCreateResponse(**response)

    async def alist_versions(
        self,
        prompt_id: str,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
        **filters,
    ) -> PromptVersionListResponse:
        """
        List versions for a specific prompt (asynchronous).

        Retrieve a paginated list of all versions for a specific prompt,
        optionally filtered by various criteria. This is useful for
        version management and history tracking.

        Args:
            prompt_id (str): The unique identifier of the prompt
            page (int, optional): Page number for pagination (1-based)
            page_size (int, optional): Number of versions per page
            **filters: Additional filter parameters such as:
                - readonly (bool): Filter by readonly status
                - model (str): Filter by AI model
                - created_after (str): Filter versions created after this date

        Returns:
            PromptVersionListResponse: A paginated list containing:
                - results (List[PromptVersion]): List of version objects
                - count (int): Total number of versions
                - next (str, optional): URL for next page if available
                - previous (str, optional): URL for previous page if available

        Raises:
            RespanError: If the prompt is not found or access is denied

        Example:
            >>> # List all versions for a prompt
            >>> versions = await client.alist_versions("prompt-123")
            >>> print(f"Prompt has {versions.count} versions")
            >>>
            >>> # List with pagination
            >>> page1 = await client.alist_versions("prompt-123", page=1, page_size=5)
            >>>
            >>> # Inspect version details
            >>> for version in versions.results[:3]:
            ...     print(f"Version {version.version}: {version.model} - {version.description}")
        """
        params = {}
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["page_size"] = page_size
        params.update(filters)

        response = await self.client.get(
            PROMPT_VERSION_LIST_PATH(prompt_id), params=params
        )

        # Handle both list and paginated response formats
        if isinstance(response, list):
            # API returns a simple list, wrap it in paginated format
            return PromptVersionListResponse(
                results=response, count=len(response), next=None, previous=None
            )
        else:
            # API returns paginated response
            return PromptVersionListResponse(**response)

    def list_versions(
        self,
        prompt_id: str,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
        **filters,
    ) -> PromptVersionListResponse:
        """List versions for a specific prompt (synchronous)."""
        params = {}
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["page_size"] = page_size
        params.update(filters)

        response = self.sync_client.get(
            PROMPT_VERSION_LIST_PATH(prompt_id), params=params
        )

        return PromptVersionListResponse(**response)

    async def aget_version(
        self, prompt_id: str, version_number: Union[int, str]
    ) -> PromptVersionRetrieveResponse:
        """
        Retrieve a specific prompt version by version number (asynchronous).

        Fetch detailed information about a specific version of a prompt,
        including all configuration parameters, messages, and metadata.

        Args:
            prompt_id (str): The unique identifier of the parent prompt
            version_number (Union[int, str]): The version number to retrieve

        Returns:
            PromptVersionRetrieveResponse: Complete version information including:
                - id (str): Unique version identifier
                - prompt_version_id (str): Unique version identifier
                - version (int): Version number
                - messages (List[Message]): Configured messages
                - model (str): AI model configuration
                - temperature (float): Model temperature setting
                - max_tokens (int): Token limit
                - All other configuration parameters

        Raises:
            RespanError: If the prompt or version is not found

        Example:
            >>> # Get specific version details
            >>> version = await client.aget_version("prompt-123", 2)
            >>> print(f"Version {version.version} uses model: {version.model}")
            >>> print(f"Temperature: {version.temperature}")
            >>>
            >>> # Inspect messages
            >>> for msg in version.messages:
            ...     print(f"{msg['role']}: {msg['content']}")
        """
        response = await self.client.get(
            f"{PROMPT_VERSION_GET_PATH(prompt_id)}/{version_number}"
        )
        return PromptVersionRetrieveResponse(**response)

    def get_version(
        self, prompt_id: str, version_number: Union[int, str]
    ) -> PromptVersionRetrieveResponse:
        """Retrieve a specific prompt version by version number (synchronous)."""
        response = self.sync_client.get(
            f"{PROMPT_VERSION_GET_PATH(prompt_id)}/{version_number}"
        )
        return PromptVersionRetrieveResponse(**response)

    async def aupdate_version(
        self,
        prompt_id: str,
        version_number: Union[int, str],
        update_data: Union[Dict[str, Any], PromptVersion],
    ) -> PromptVersionRetrieveResponse:
        """
        Update an existing prompt version's properties (asynchronous).

        Modify version configuration such as model parameters, messages,
        description, and other settings. Some fields may be read-only
        depending on the version state.

        Args:
            prompt_id (str): The unique identifier of the parent prompt
            version_number (Union[int, str]): The version number to update
            update_data (Union[Dict[str, Any], PromptVersion]): Update parameters containing:
                - description (str, optional): New version description
                - readonly (bool, optional): Set readonly status
                - messages (List[Message], optional): Updated messages
                - model (str, optional): New AI model
                - temperature (float, optional): New temperature setting
                - And other configuration parameters...

        Returns:
            PromptVersionRetrieveResponse: The updated version object

        Raises:
            RespanError: If the prompt/version is not found, update fails,
                or invalid parameters are provided

        Example:
            >>> from respan_sdk.respan_types.prompt_types import PromptVersion
            >>>
            >>> # Update version configuration
            >>> update_data = PromptVersion(
            ...     description="Updated version with better prompts",
            ...     temperature=0.8,
            ...     max_tokens=3000,
            ...     readonly=True
            ... )
            >>> updated_version = await client.aupdate_version("prompt-123", 1, update_data)
            >>> print(f"Updated version {updated_version.version}")
        """
        # Validate and prepare the input data
        validated_data = self._validate_input(update_data, PromptVersion, partial=True)

        response = await self.client.patch(
            f"{PROMPT_VERSION_UPDATE_PATH(prompt_id)}/{version_number}",
            json_data=self._prepare_json_data(validated_data, partial=True),
        )
        return PromptVersionRetrieveResponse(**response)

    def update_version(
        self,
        prompt_id: str,
        version_number: Union[int, str],
        update_data: Union[Dict[str, Any], PromptVersion],
    ) -> PromptVersionRetrieveResponse:
        """Update an existing prompt version's properties (synchronous)."""
        # Validate and prepare the input data
        validated_data = self._validate_input(update_data, PromptVersion, partial=True)

        response = self.sync_client.patch(
            f"{PROMPT_VERSION_UPDATE_PATH(prompt_id)}/{version_number}",
            json_data=self._prepare_json_data(validated_data, partial=True),
        )
        return PromptVersionRetrieveResponse(**response)


def create_prompt_client(api_key: str, base_url: str = None) -> PromptAPI:
    """
    Create a unified prompt API client

    Args:
        api_key: Keywords AI API key
        base_url: Base URL for the API (default: KEYWORDS_AI_DEFAULT_BASE_URL)

    Returns:
        PromptAPI client instance with both sync and async methods
    """
    return PromptAPI(api_key=api_key, base_url=base_url)


# For backward compatibility, create aliases
SyncPromptAPI = PromptAPI  # Same class, just different name for clarity in imports

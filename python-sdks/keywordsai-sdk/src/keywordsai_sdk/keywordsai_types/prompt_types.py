from pydantic import Field, ConfigDict
from typing import Any, List, Union, Dict, Optional
from datetime import datetime
from .base_types import KeywordsAIBaseModel
from ._internal_types import Message
from .generic_types import PaginatedResponseType


class PromptVersion(KeywordsAIBaseModel):
    """Prompt version type based on Django model and API responses"""

    id: Optional[Union[int, str]] = None
    prompt_version_id: str = ""
    description: Optional[str] = ""
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    version: int = 0
    messages: List[Message] = []
    edited_by: Optional[Dict[str, Any]] = None
    model: str = "gpt-3.5-turbo"
    stream: bool = False
    temperature: float = 0.7
    max_tokens: int = 4096
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    reasoning_effort: Optional[str] = None
    variables: Dict[str, Any] = {}
    readonly: bool = False
    fallback_models: Optional[List[str]] = None
    load_balance_models: Optional[List[Dict[str, Any]]] = None
    tools: Optional[List[Dict[str, Any]]] = None
    tool_choice: Optional[Union[str, Dict[str, Any]]] = None
    response_format: Optional[Dict[str, Any]] = None
    json_schema: Optional[Dict[str, Any]] = None
    is_enforcing_response_format: bool = False
    prompt: Optional[Union[int, str]] = None  # Reference to parent prompt
    parent_prompt: Optional[str] = None  # Parent prompt ID

    model_config = ConfigDict(from_attributes=True, extra="allow")


class Prompt(KeywordsAIBaseModel):
    """Main prompt type"""

    id: Optional[Union[int, str]] = None
    name: str = "Untitled"
    description: str = ""
    prompt_id: str = ""
    prompt_slug: Optional[str] = ""
    full_prompt_id: Optional[str] = None  # Same as prompt_id in responses
    current_version: Optional[PromptVersion] = None
    live_version: Optional[PromptVersion] = None
    prompt_versions: Optional[List[PromptVersion]] = None
    prompt_activities: Optional[List[Dict[str, Any]]] = None
    commit_count: int = 0
    starred: bool = False
    tags: List[Dict[str, Any]] = []

    model_config = ConfigDict(from_attributes=True, extra="allow")


# Response types for different API endpoints
class PromptCreateResponse(Prompt):
    """Response type for prompt creation"""

    pass


class PromptListResponse(PaginatedResponseType[Prompt]):
    """Response type for prompt listing"""

    pass


class PromptRetrieveResponse(Prompt):
    """Response type for prompt retrieval"""

    pass


class PromptVersionCreateResponse(PromptVersion):
    """Response type for prompt version creation"""

    pass


class PromptVersionListResponse(PaginatedResponseType[PromptVersion]):
    """Response type for prompt version listing"""

    pass


class PromptVersionRetrieveResponse(PromptVersion):
    """Response type for prompt version retrieval"""

    pass

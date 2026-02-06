# Re-export all prompt constants from respan-sdk
from respan_sdk.constants.prompt_constants import (
    # Message role types
    MessageRoleType,
    # Response format types
    ResponseFormatType,
    # Tool choice types
    ToolChoiceType,
    # Reasoning effort types
    ReasoningEffortType,
    # Activity types
    ACTIVITY_TYPE_PROMPT_CREATION,
    ACTIVITY_TYPE_COMMIT,
    ACTIVITY_TYPE_UPDATE,
    ACTIVITY_TYPE_DELETE,
    ActivityType,
    # Default model
    DEFAULT_MODEL,
)

# Base paths
PROMPT_BASE_PATH = "/api/prompts"

# Specific endpoints
PROMPT_CREATION_PATH = f"{PROMPT_BASE_PATH}"
PROMPT_LIST_PATH = f"{PROMPT_BASE_PATH}/list"
PROMPT_GET_PATH = f"{PROMPT_BASE_PATH}"
PROMPT_UPDATE_PATH = f"{PROMPT_BASE_PATH}"
PROMPT_DELETE_PATH = f"{PROMPT_BASE_PATH}"

# Prompt version management endpoints
PROMPT_VERSION_CREATION_PATH = (
    lambda prompt_id: f"{PROMPT_BASE_PATH}/{prompt_id}/versions"
)
PROMPT_VERSION_LIST_PATH = lambda prompt_id: f"{PROMPT_BASE_PATH}/{prompt_id}/versions"
PROMPT_VERSION_GET_PATH = lambda prompt_id: f"{PROMPT_BASE_PATH}/{prompt_id}/versions"
PROMPT_VERSION_UPDATE_PATH = (
    lambda prompt_id: f"{PROMPT_BASE_PATH}/{prompt_id}/versions"
)

__all__ = [
    # Message role types
    "MessageRoleType",
    # Response format types
    "ResponseFormatType",
    # Tool choice types
    "ToolChoiceType",
    # Reasoning effort types
    "ReasoningEffortType",
    # Activity types
    "ACTIVITY_TYPE_PROMPT_CREATION",
    "ACTIVITY_TYPE_COMMIT",
    "ACTIVITY_TYPE_UPDATE",
    "ACTIVITY_TYPE_DELETE",
    "ActivityType",
    # Default model
    "DEFAULT_MODEL",
    # Prompt paths
    "PROMPT_BASE_PATH",
    "PROMPT_CREATION_PATH",
    "PROMPT_LIST_PATH",
    "PROMPT_GET_PATH",
    "PROMPT_UPDATE_PATH",
    "PROMPT_DELETE_PATH",
    # Prompt version paths
    "PROMPT_VERSION_CREATION_PATH",
    "PROMPT_VERSION_LIST_PATH",
    "PROMPT_VERSION_GET_PATH",
    "PROMPT_VERSION_UPDATE_PATH",
]

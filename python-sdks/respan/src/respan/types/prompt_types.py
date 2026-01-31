"""
Prompt Type Definitions for Keywords AI SDK

This module provides comprehensive type definitions for prompt operations in Keywords AI.
All types are Pydantic models that provide validation, serialization, and clear structure
for API interactions.

🏗️ CORE TYPES:

Prompt: Complete prompt information returned by the API
PromptVersion: Prompt version information with configuration details
PromptCreateResponse: Response type for prompt creation
PromptListResponse: Paginated list of prompts
PromptRetrieveResponse: Response type for prompt retrieval
PromptVersionCreateResponse: Response type for prompt version creation
PromptVersionListResponse: Paginated list of prompt versions
PromptVersionRetrieveResponse: Response type for prompt version retrieval

💡 USAGE PATTERNS:

1. CREATING PROMPTS:
   Use Prompt to create new prompts with basic information like name and description.

2. MANAGING VERSIONS:
   Use PromptVersion to create and manage different versions of prompts with
   specific configurations, messages, and model parameters.

3. LISTING PROMPTS:
   PromptListResponse provides paginated results with navigation metadata.

4. VERSION MANAGEMENT:
   PromptVersionListResponse provides paginated results for prompt versions.

📖 EXAMPLES:

Basic prompt creation:
    >>> from respan.types.prompt_types import Prompt
    >>> 
    >>> # Create a basic prompt
    >>> prompt = Prompt(
    ...     name="Customer Support Assistant",
    ...     description="AI assistant for customer support queries",
    ...     prompt_id="cust-support-001"
    ... )

Prompt version with configuration:
    >>> from respan.types.prompt_types import PromptVersion
    >>> from datetime import datetime
    >>> 
    >>> # Create a prompt version with specific configuration
    >>> version = PromptVersion(
    ...     prompt_version_id="version-001",
    ...     description="Initial version with basic configuration",
    ...     created_at=datetime.utcnow(),
    ...     updated_at=datetime.utcnow(),
    ...     version=1,
    ...     messages=[
    ...         {"role": "system", "content": "You are a helpful customer support assistant."},
    ...         {"role": "user", "content": "How can I help you today?"}
    ...     ],
    ...     model="gpt-4o-mini",
    ...     temperature=0.7,
    ...     max_tokens=2048
    ... )

🔧 FIELD REFERENCE:

Prompt Fields:
- id (int|str, optional): Unique identifier
- name (str): Human-readable prompt name
- description (str): Detailed description of prompt purpose
- prompt_id (str): Unique prompt identifier
- prompt_slug (str, optional): URL-friendly slug
- current_version (PromptVersion, optional): Current active version
- live_version (PromptVersion, optional): Live/published version
- prompt_versions (List[PromptVersion], optional): All versions
- commit_count (int): Number of commits/versions
- starred (bool): Whether prompt is starred
- tags (List[Dict]): Associated tags

PromptVersion Fields:
- id (int|str, optional): Unique identifier
- prompt_version_id (str): Unique version identifier
- description (str, optional): Version description
- created_at (datetime): Creation timestamp
- updated_at (datetime): Last update timestamp
- version (int): Version number
- messages (List[Message]): Conversation messages
- model (str): AI model to use (default: "gpt-3.5-turbo")
- temperature (float): Model temperature (0.0-2.0)
- max_tokens (int): Maximum tokens to generate
- top_p (float): Nucleus sampling parameter
- frequency_penalty (float): Frequency penalty (-2.0 to 2.0)
- presence_penalty (float): Presence penalty (-2.0 to 2.0)
- reasoning_effort (str, optional): Reasoning effort level
- variables (Dict): Template variables
- readonly (bool): Whether version is read-only
- fallback_models (List[str], optional): Fallback model list
- tools (List[Dict], optional): Available tools
- tool_choice (str|Dict, optional): Tool choice strategy
- response_format (Dict, optional): Response format specification

⚠️ IMPORTANT NOTES:
- All datetime fields should be timezone-aware
- Model parameters affect AI behavior and costs
- Messages follow OpenAI chat format
- Variables enable prompt templating
- Tools enable function calling capabilities
"""

# Re-export all prompt types from respan-sdk
from respan_sdk.respan_types.prompt_types import (
    Prompt,
    PromptVersion,
    PromptCreateResponse,
    PromptListResponse,
    PromptRetrieveResponse,
    PromptVersionCreateResponse,
    PromptVersionListResponse,
    PromptVersionRetrieveResponse,
)

__all__ = [
    "Prompt",
    "PromptVersion",
    "PromptCreateResponse",
    "PromptListResponse",
    "PromptRetrieveResponse",
    "PromptVersionCreateResponse",
    "PromptVersionListResponse",
    "PromptVersionRetrieveResponse",
]

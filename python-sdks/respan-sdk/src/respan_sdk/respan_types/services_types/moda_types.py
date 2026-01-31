"""
Moda API type definitions for ingestion.

Based on: https://docs.modaflows.com/ingestion/direct-api
"""
from typing import Optional, Literal, List, Dict, Any
from pydantic import Field
from respan_sdk.respan_types._internal_types import RespanBaseModel


class ModaEvent(RespanBaseModel):
    """
    Single event to be sent to Moda ingestion API.
    
    Required fields:
    - conversation_id: Unique ID for the conversation
    - role: One of "user", "assistant", "system"
    - message: The message content
    
    Optional fields include token counts, model info, timestamps, and structured content blocks.
    """
    # Required fields
    conversation_id: str = Field(description="Unique ID for the conversation")
    role: Literal["user", "assistant", "system"] = Field(description="Message role")
    message: str = Field(description="The message content")
    
    # Optional fields
    timestamp: Optional[str] = Field(default=None, description="ISO 8601 timestamp (defaults to now)")
    trace_id: Optional[str] = Field(default=None, description="For linking related events (defaults to conversation_id)")
    user_id: Optional[str] = Field(default=None, description="Identifier for the end user")
    
    # Token usage
    input_tokens: Optional[int] = Field(default=None, description="Number of input/prompt tokens used")
    output_tokens: Optional[int] = Field(default=None, description="Number of output/completion tokens used")
    reasoning_tokens: Optional[int] = Field(default=None, description="Tokens used for extended thinking (Claude models)")
    
    # Model information
    model: Optional[str] = Field(default=None, description="Model name (e.g., gpt-4o, claude-3-opus)")
    provider: Optional[str] = Field(default=None, description="Provider name (e.g., openai, anthropic)")
    
    # Structured content blocks
    # Each block is a dict with "type" field and type-specific fields:
    # - {"type": "text", "text": "..."} - Plain text content
    # - {"type": "thinking", "text": "..."} - Model reasoning (extended thinking)
    # - {"type": "tool_use", "tool_name": "...", "tool_use_id": "...", "input": {...}} - Tool/function call
    # - {"type": "tool_result", "tool_use_id": "...", "content": "...", "is_error": bool} - Tool response
    # - {"type": "image", "source": "..."} - Image (base64 or URL)
    content_blocks: Optional[List[Dict[str, Any]]] = Field(default=None, description="Structured content blocks")


class ModaIngestRequest(RespanBaseModel):
    """
    Request payload for Moda ingest API.
    
    POST https://moda-ingest.modas.workers.dev/v1/ingest
    """
    events: List[ModaEvent] = Field(description="Array of events to ingest")


class ModaParams(RespanBaseModel):
    """
    Parameters for Moda integration in Keywords AI.
    
    This is what users pass in the respan_params.moda_params field.
    
    Users only need to provide their Moda API key - we automatically
    construct the events from the log data they're already sending.
    """
    api_key: Optional[str] = Field(default=None, description="Moda API key for authentication")


__all__ = [
    "ModaEvent",
    "ModaIngestRequest",
    "ModaParams",
]

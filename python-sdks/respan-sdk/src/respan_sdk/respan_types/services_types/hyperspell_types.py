"""
Type definitions for Hyperspell integration payloads.
"""

from typing import Any, Dict, List, Optional, Union

from pydantic import ConfigDict

from respan_sdk.respan_types.base_types import RespanBaseModel


class HyperspellAddMemoryParams(RespanBaseModel):
    """Schema for one /memories/add payload item."""

    text: str
    resource_id: Optional[str] = None
    collection: Optional[str] = None
    title: Optional[str] = None
    date: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(extra="allow")


class HyperspellSearchMemoriesParams(RespanBaseModel):
    """Schema for /memories/query payload."""

    query: str
    answer: Optional[bool] = None
    sources: Optional[List[str]] = None
    options: Optional[Dict[str, Any]] = None
    max_results: Optional[int] = None

    model_config = ConfigDict(extra="allow")


class HyperspellParams(RespanBaseModel):
    """Top-level request schema for hyperspell_params."""

    api_key: Optional[str] = None
    user_id: Optional[str] = None
    add_memory: Optional[
        Union[HyperspellAddMemoryParams, List[HyperspellAddMemoryParams]]
    ] = None
    search_memories: Optional[HyperspellSearchMemoriesParams] = None

    model_config = ConfigDict(extra="allow")

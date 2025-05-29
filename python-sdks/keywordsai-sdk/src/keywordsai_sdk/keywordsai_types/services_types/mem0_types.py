from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, model_validator, ConfigDict
from datetime import datetime

class Message(BaseModel):
    role: str
    content: str

class ComparisonOperator(BaseModel):
    in_: Optional[List[Any]] = Field(None, alias="in")
    gte: Optional[str] = None
    lte: Optional[str] = None
    gt: Optional[str] = None
    lt: Optional[str] = None
    ne: Optional[str] = None
    contains: Optional[str] = None
    icontains: Optional[str] = None

class FilterCondition(BaseModel):
    user_id: Optional[Union[str, ComparisonOperator]] = None
    agent_id: Optional[Union[str, ComparisonOperator]] = None
    app_id: Optional[Union[str, ComparisonOperator]] = None
    run_id: Optional[Union[str, ComparisonOperator]] = None
    created_at: Optional[Union[str, ComparisonOperator]] = None
    updated_at: Optional[Union[str, ComparisonOperator]] = None
    text: Optional[Union[str, ComparisonOperator]] = None
    categories: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

class SearchFilters(BaseModel):
    AND: Optional[List[FilterCondition]] = None
    OR: Optional[List[FilterCondition]] = None

class Mem0ClientConfig(BaseModel):
    api_key: Optional[str] = None
    org_id: Optional[str] = None
    project_id: Optional[str] = None
    host: Optional[str] = None

    @model_validator(mode="after")
    def validate_org_id_and_project_id(self):
        if self.org_id or self.project_id:
            if not all([self.org_id, self.project_id]):
                raise ValueError("org_id and project_id must be provided together")
        return self
    
    model_config = ConfigDict(extra="ignore")

class Mem0RunTimeIdentification(BaseModel):
    """
    Common identification parameters used across Mem0 API operations.
    """
    user_id: Optional[str] = None
    agent_id: Optional[str] = None
    app_id: Optional[str] = None
    run_id: Optional[str] = None

class AddMemoriesParams(BaseModel):
    """Parameters specific to adding memories to Mem0"""
    messages: List[Message]
    metadata: Optional[Dict[str, Any]] = None
    includes: Optional[str] = Field(None, min_length=1)
    excludes: Optional[str] = Field(None, min_length=1)
    infer: bool = True
    output_format: Optional[str] = None
    custom_categories: Optional[Dict[str, Any]] = None
    custom_instructions: Optional[str] = None
    immutable: bool = False
    expiration_date: Optional[str] = None
    version: Optional[str] = "v1"

class SearchMemoriesParams(BaseModel):
    """Parameters specific to searching memories in Mem0"""
    query: str
    filters: Optional[SearchFilters] = None
    top_k: int = 10
    fields: Optional[List[str]] = None
    rerank: bool = False
    keyword_search: bool = False
    filter_memories: bool = False
    threshold: float = 0.3
    version: Optional[str] = "v2"

class Mem0Params(Mem0ClientConfig, Mem0RunTimeIdentification):
    """
    Mem0 integration parameters for KeywordsAI.
    
    This allows users to configure memory operations using endpoint-specific configurations.
    Users can reference outputs from one endpoint in another using the {{variable.var_att}} syntax.
    Common identification parameters (api_key, org_id, etc.) are inherited from Mem0Identification.
    """
    add_memories: Optional[AddMemoriesParams] = None
    search_memories: Optional[SearchMemoriesParams] = None
    
    @model_validator(mode="after")
    def validate_at_least_one_operation(cls, model: "Mem0Params"):
        """Ensure at least one operation is configured"""
        if not any([model.add_memories, model.search_memories]):
            raise ValueError("At least one Mem0 operation (add_memories or search_memories) must be configured")
        return model

class MemoryData(BaseModel):
    memory: str

class MemoryResponse(BaseModel):
    id: str
    data: MemoryData
    event: str

class AddMemoriesResponse(BaseModel):
    memories: List[MemoryResponse]

class SearchMemory(BaseModel):
    id: str
    memory: str
    user_id: str
    metadata: Optional[Dict[str, Any]] = None
    categories: List[str]
    immutable: bool = False
    expiration_date: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class SearchMemoriesResponse(BaseModel):
    memories: List[SearchMemory]

from typing import List, Literal, Optional
from typing_extensions import TypedDict
from pydantic import BaseModel, ConfigDict, field_validator
from ._internal_types import KeywordsAIParams, BasicLLMParams, KeywordsAIBaseModel, Customer
"""
Conventions:

1. KeywordsAI as a prefix to class names
2. Params as a suffix to class names

Logging params types:
1. TEXT
2. EMBEDDING
3. AUDIO
4. GENERAL_FUNCTION
"""
class KeywordsAITextLogParams(KeywordsAIParams, BasicLLMParams):

    @field_validator("customer_params", mode="after")
    def validate_customer_params(cls, v: Customer):
        if v.customer_identifier is None:
            return None
        return v

    model_config = ConfigDict(from_attributes=True)

class SimpleLogStats(KeywordsAIBaseModel):
    """
    Add default values to account for cases of error logs
    """
    total_request_tokens: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cost: float = 0
    organization_id: int
    user_id: int
    organization_key_id: str
    model: str | None = None
    metadata: dict | None = None
    used_custom_credential: bool = False

    def __init__(self, **data):
        for field_name in self.__annotations__:
            if field_name.endswith('_id'):
                related_model_name = field_name[:-3]  # Remove '_id' from the end
                self._assign_related_field(related_model_name, field_name, data)
        
        super().__init__(**data)

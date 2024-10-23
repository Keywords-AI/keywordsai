from pydantic import BaseModel, field_validator
from typing import Any, Optional, List, Union, Dict
from typing_extensions import Literal, TypedDict

class LBProviderCredentialDictType(TypedDict):
    weight: float
    credentials: dict
class LBProviderCredentialType(BaseModel):
    weight: float
    credentials: dict
    
    @field_validator("weight")
    def weight_validator(cls, v):
        if v <= 0:
            raise ValueError("Weight must be greater than 0")
        return v
    
    def model_dump(self, *args, **kwargs)-> LBProviderCredentialDictType:
        kwargs["exclude_none"] = True
        return super().model_dump(*args, **kwargs)
    
class LBProviderCredentialDictType(TypedDict):
    weight: float
    credentials: dict
    
ProviderCredentialType = Union[List[LBProviderCredentialType], dict]
ProviderCredentialDictType = Union[List[LBProviderCredentialDictType], dict]

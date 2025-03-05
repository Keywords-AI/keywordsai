from pydantic import BaseModel
from typing import Literal, Optional, Union

class RangeType(BaseModel):
    min: float
    max: float

class ParamType(BaseModel): # A type for defining a parameter for a function
    name: str
    type: Literal["string", "number", "boolean", "object", "array", "int"] = "string"
    default: Optional[Union[str, int, bool, dict, list, float]] = None
    range: Optional[RangeType] = None
    description: Optional[str] = None
    required: Optional[bool] = False
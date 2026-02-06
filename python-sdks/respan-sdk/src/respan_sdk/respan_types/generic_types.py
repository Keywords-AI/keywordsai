from pydantic import BaseModel
from typing import Literal, Optional, Union, Generic, TypeVar, List
from respan_sdk.respan_types.base_types import RespanBaseModel


class RangeType(BaseModel):
    min: float
    max: float


class ParamType(BaseModel):  # A type for defining a parameter for a function
    name: str
    type: Literal["string", "number", "boolean", "object", "array", "int"] = "string"
    default: Optional[Union[str, int, bool, dict, list, float]] = None
    range: Optional[RangeType] = None
    description: Optional[str] = None
    required: Optional[bool] = False


T = TypeVar("T")


class PaginatedResponseType(RespanBaseModel, Generic[T]):
    """
    Paginated response type for paginated queries
    """

    results: List[T]
    count: int
    next: Optional[str] = None
    previous: Optional[str] = None

from respan_sdk.respan_types.log_types import (
    RespanLogParams,
    RespanFullLogParams,
)
from respan.types.generic_types import PaginatedResponseType

# Type alias for log list responses using the generic paginated type
LogList = PaginatedResponseType[RespanFullLogParams]

__all__ = [
    "RespanLogParams",
    "RespanFullLogParams", 
    "LogList",
]
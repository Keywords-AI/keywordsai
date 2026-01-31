from keywordsai_sdk.keywordsai_types.log_types import (
    KeywordsAILogParams,
    KeywordsAIFullLogParams,
)
from keywordsai.types.generic_types import PaginatedResponseType

# Type alias for log list responses using the generic paginated type
LogList = PaginatedResponseType[KeywordsAIFullLogParams]

__all__ = [
    "KeywordsAILogParams",
    "KeywordsAIFullLogParams", 
    "LogList",
]
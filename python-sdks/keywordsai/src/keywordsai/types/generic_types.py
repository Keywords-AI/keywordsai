from keywordsai_sdk.keywordsai_types.base_types import KeywordsAIBaseModel
from typing import List, Optional, Generic, TypeVar


T = TypeVar('T')

class PaginatedResponseType(KeywordsAIBaseModel, Generic[T]):
    """
    Paginated response type for paginated queries
    """
    results: List[T]
    count: int
    next: Optional[str] = None
    previous: Optional[str] = None
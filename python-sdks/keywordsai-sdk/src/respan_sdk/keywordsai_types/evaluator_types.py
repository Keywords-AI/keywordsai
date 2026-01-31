from datetime import datetime
from keywordsai_sdk.keywordsai_types.base_types import KeywordsAIBaseModel
from keywordsai_sdk.keywordsai_types.generic_types import PaginatedResponseType


class Evaluator(KeywordsAIBaseModel):
    """Evaluator model"""

    id: str
    name: str
    slug: str
    description: str = ""
    created_at: datetime
    updated_at: datetime


EvaluatorList = PaginatedResponseType[Evaluator]

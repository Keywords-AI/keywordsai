from datetime import datetime
from respan_sdk.respan_types.base_types import RespanBaseModel
from respan_sdk.respan_types.generic_types import PaginatedResponseType


class Evaluator(RespanBaseModel):
    """Evaluator model"""

    id: str
    name: str
    slug: str
    description: str = ""
    created_at: datetime
    updated_at: datetime


EvaluatorList = PaginatedResponseType[Evaluator]

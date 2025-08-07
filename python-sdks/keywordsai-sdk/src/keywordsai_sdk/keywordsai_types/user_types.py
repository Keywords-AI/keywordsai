from pydantic import ConfigDict
from .base_types import KeywordsAIBaseModel


class EditorType(KeywordsAIBaseModel):
    """User information for edited_by fields"""

    first_name: str
    last_name: str
    email: str


    model_config = ConfigDict(from_attributes=True)
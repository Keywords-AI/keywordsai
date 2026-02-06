from pydantic import ConfigDict
from .base_types import RespanBaseModel


class EditorType(RespanBaseModel):
    """User information for edited_by fields"""

    first_name: str
    last_name: str
    email: str


    model_config = ConfigDict(from_attributes=True)
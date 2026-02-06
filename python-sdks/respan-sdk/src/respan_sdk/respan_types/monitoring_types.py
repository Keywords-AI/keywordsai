from respan_sdk.respan_types.base_types import RespanBaseModel

class ConditionParams(RespanBaseModel):
    condition_id: str
    condition_slug: str = None
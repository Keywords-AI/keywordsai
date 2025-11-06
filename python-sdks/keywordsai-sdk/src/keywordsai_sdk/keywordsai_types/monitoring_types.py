from keywordsai_sdk.keywordsai_types.base_types import KeywordsAIBaseModel

class ConditionParams(KeywordsAIBaseModel):
    condition_id: str
    condition_slug: str = None
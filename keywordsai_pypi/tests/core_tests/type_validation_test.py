from keywordsai_sdk.keywordsai_types.param_types import KeywordsAITextLogParams

params = KeywordsAITextLogParams.model_validate({"customer_params": {"customer_identifier": None}})

params
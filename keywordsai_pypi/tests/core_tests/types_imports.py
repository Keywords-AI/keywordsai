from keywordsai_sdk.keywordsai_types.param_types import KeywordsAITextLogParams
from keywordsai_sdk.utils import separate_params

params = {
    "model": "gpt-3.5-turbo",
    "customer_identifier": "sdk_customer",
    "keywordsai_api_controls": {
        "bullshit": None
    }
}

oai_params, kai_params = separate_params(params, raise_exception=True)

print(oai_params, kai_params)
from respan_sdk.respan_types.param_types import RespanTextLogParams
from respan_sdk.utils import separate_params

params = {
    "model": "gpt-3.5-turbo",
    "customer_identifier": "sdk_customer",
    "respan_api_controls": {
        "bullshit": None
    }
}

oai_params, kai_params = separate_params(params, raise_exception=True)

print(oai_params, kai_params)
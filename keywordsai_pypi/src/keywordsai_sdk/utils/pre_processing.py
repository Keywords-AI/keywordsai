from keywordsai_sdk.keywordsai_types._internal_types import KeywordsAIParams, RetryParams, EvaluationParams, BasicLLMParams, KeywordsAIAPIControlParams
from pydantic import BaseModel, ValidationError
from typing import Literal




def assign_with_validation(
    retrieve_from: dict,
    assign_to: dict,
    key,
    type: BaseModel,
    raise_exception=False,
    mode: Literal["assign", "override"] = "assign",
):
    """
    Input:
    retrieve_from: dict, the dictionary to retrieve the value from
    assign_to: dict, the dictionary to assign the value to
    key: str, the key to retrieve the value from
    type: BaseModel, the type to validate the value
    raise_exception: bool, whether to raise an exception if the value is invalid
    """
    try:
        params = retrieve_from.pop(key, {})
        params = type.model_validate(params).model_dump()
        if mode == "assign":
            assign_to[key] = params
        elif mode == "override":
            assign_to.update(params)
    except ValidationError as e:
        print(f"Validation error: {e.errors(include_url=False)}")
        if raise_exception:
            raise e
        return False
    except Exception as e:
        if raise_exception:
            raise e
        return False


def separate_params(params: dict, remove_none=True, raise_exception=False):
    """
    Separate the params into llm_params and keywordsai_params
    If the params are falsely, they are removed from the dictionary (no params are valid with value 0)
    Returns:
    llm_params: dict
    keywordsai_params: dict

    RULES:
        1. For cleanliness, all params that are default as False should end with "or None" as fallback so that they get removed
    """

    keywordsai_params = {}
    keywordsai_params["cache_enabled"] = params.pop("cache_enabled", None) or None
    keywordsai_params["cache_options"] = params.pop("cache_options", None) or None
    keywordsai_params["cache_ttl"] = (
        params.pop("cache_ttl", None) or None
    )  # Avoid unwanted 0
    keywordsai_params["calling_model"] = params.get(
        "model", None
    )  # We want to make a copy of the model the user is calling, not remove
    keywordsai_params["credential_override"] = (
        params.pop("credential_override", None) or None
    )
    keywordsai_params["customer_credentials"] = (
        params.pop("customer_credentials", None) or None
    )
    keywordsai_params["customer_email"] = params.pop("customer_email", "") or None
    keywordsai_params["customer_identifier"] = (
        params.pop("customer_identifier", "") or None
    )
    keywordsai_params["customer_params"] = params.pop("customer_params", None) or None
    keywordsai_params["delimiter"] = params.pop("delimiter", "\n\n") or "---"
    keywordsai_params["disable_fallback"] = params.pop("disable_fallback", None)
    keywordsai_params["disable_log"] = params.pop("disable_log", None) or None
    if "evaluation_params" in params:
        assign_with_validation(
            retrieve_from=params,
            assign_to=keywordsai_params,
            key="evaluation_params",
            type=EvaluationParams,
            raise_exception=raise_exception,
            mode="assign",
        )
    keywordsai_params["evaluation_identifier"] = (
        params.pop("evaluation_identifier", "") or None
    )
    keywordsai_params["exclude_models"] = params.pop("exclude_models", None) or None
    keywordsai_params["exclude_providers"] = (
        params.pop("exclude_providers", None) or None
    )
    keywordsai_params["fallback_models"] = params.pop("fallback_models", None) or None
    keywordsai_params["field_name"] = params.pop("field_name", "data: ") or ""
    keywordsai_params["for_eval"] = params.pop("for_eval", None) or None
    keywordsai_params["generation_time"] = (
        params.pop("generation_time", None) or None
    )  # Avoid unwanted 0
    keywordsai_params["headers"] = params.pop("headers", None)
    keywordsai_params["ip_address"] = params.pop("ip_address", None)
    assign_with_validation(
        retrieve_from=params,
        assign_to=keywordsai_params,
        key="keywordsai_api_controls",
        type=KeywordsAIAPIControlParams,
        raise_exception=raise_exception,
    )

    keywordsai_params["latency"] = params.pop("latency", None) or None
    keywordsai_params["load_balance_group"] = (
        params.pop("load_balance_group", None) or None
    )
    keywordsai_params["load_balance_models"] = (
        params.pop("load_balance_models", None) or None
    )
    keywordsai_params["metadata"] = params.pop("metadata", None) or None
    keywordsai_params["model_name_map"] = params.pop("model_name_map", None) or None
    keywordsai_params["posthog_integration"] = (
        params.pop("posthog_integration", None) or None
    )
    keywordsai_params["prompt"] = params.pop("prompt", None) or None
    keywordsai_params["prompt_group_id"] = params.pop("prompt_group_id", None) or None
    keywordsai_params["request_breakdown"] = params.pop("request_breakdown", None)
    if "retry_params" in params:
        assign_with_validation(
            retrieve_from=params,
            assign_to=keywordsai_params,
            key="retry_params",
            type=RetryParams,
            raise_exception=raise_exception,
            mode="override",
        )
    keywordsai_params["thread_identifier"] = params.pop("thread_identifier", "") or None
    keywordsai_params["time_to_first_token"] = (
        params.pop("time_to_first_token", None) or None
    )  # Avoid unwanted 0
    keywordsai_params["trace_params"] = params.pop("trace_params", None) or None
    keywordsai_params["ttft"] = params.pop("ttft", None) or None
    # Special case does not follow alphabetical order because it needs to override everything
    if "keywordsai_params" in params:
        assign_with_validation(
            retrieve_from=params,
            assign_to=keywordsai_params,
            key="keywordsai_params",
            type=KeywordsAIParams,
            raise_exception=raise_exception,
            mode="override",
        )

    # prompt_params = params.pop("prompt_params", {})
    # llm_params = {}
    # prompt_configs: dict | None = keywordsai_params.get("prompt", {})
    # override = prompt_configs and prompt_configs.get("override", False)
    # if override:
    #     llm_params.update(params)
    #     llm_params.update(prompt_params)
    # else:
    #     llm_params.update(prompt_params)
    #     llm_params.update(params)

    if remove_none:
        params = {k: v for k, v in params.items() if v is not None}
        keywordsai_params = {
            k: v for k, v in keywordsai_params.items() if v is not None
        }

    return params, keywordsai_params

def validate_and_separate_params(params: dict) -> tuple[BasicLLMParams, KeywordsAIParams]:
    """
    Validate and separate the params into llm_params and keywordsai_params using Pydantic models
    Returns:
    basic_llm: BasicLLMParams
    keywords_ai: KeywordsAIParams
    """

    basic_llm = BasicLLMParams.model_validate(params)
    keywords_ai = KeywordsAIParams.model_validate(params)

    return basic_llm, keywords_ai

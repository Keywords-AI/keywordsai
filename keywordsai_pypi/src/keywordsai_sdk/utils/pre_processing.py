from keywordsai_sdk.keywordsai_types._internal_types import KeywordsAIParams


def separate_params(params: dict, remove_none=True):
    """
    Separate the params into llm_params and keywordsai_params
    If the params are falsely, they are removed from the dictionary (no params are valid with value 0)
    Returns:
    llm_params: dict
    keywordsai_params: dict
    """

    keywordsai_params = {}
    keywordsai_params["calling_model"] = params.get("model", None) # We want to make a copy of the model the user is calling, not remove
    keywordsai_params["request_breakdown"] = params.pop("request_breakdown", None)
    keywordsai_params["ip_address"] = params.pop("ip_address", None)
    keywordsai_params["headers"] = params.pop("headers", None)
    keywordsai_params["cache_options"] = params.pop("cache_options", None) or None
    keywordsai_params["customer_credentials"] = (
        params.pop("customer_credentials", None) or None
    )
    keywordsai_params["disable_fallback"] = params.pop("disable_fallback", None)
    keywordsai_params["credential_override"] = (
        params.pop("credential_override", None) or None
    )
    keywordsai_params["load_balance_models"] = (
        params.pop("load_balance_models", None) or None
    )
    keywordsai_params["exclude_models"] = params.pop("exclude_models", None) or None
    keywordsai_params["exclude_providers"] = params.pop("exclude_providers", None) or None
    keywordsai_params["fallback_models"] = params.pop("fallback_models", None) or None
    keywordsai_params["for_eval"] = params.pop("for_eval", None)
    keywordsai_params["metadata"] = params.pop("metadata", None) or None
    keywordsai_params["disable_log"] = params.pop("disable_log", None)
    keywordsai_params["load_balance_group"] = params.pop("load_balance_group", None) or None
    keywordsai_params["trace_params"] = params.pop("trace_params", None) or None
    keywordsai_params["posthog_integration"] = params.pop("posthog_integration", None) or None
    keywordsai_params["customer_identifier"] = (
        params.pop("customer_identifier", "") or None
    )
    keywordsai_params["evaluation_identifier"] = (
        params.pop("evaluation_identifier", "") or None 
    )
    keywordsai_params["model_name_map"] = params.pop("model_name_map", None) or None
    keywordsai_params["thread_identifier"] = params.pop("thread_identifier", "") or None
    keywordsai_params["customer_email"] = params.pop("customer_email", "") or None
    keywordsai_params["delimiter"] = params.pop("delimiter", "\n\n") or "---"
    keywordsai_params["field_name"] = params.pop("field_name", "data: ") or ""
    keywordsai_params["prompt"] = params.pop("prompt", None) or None
    keywordsai_params["customer_params"] = params.pop("customer_params", None) or None
    keywordsai_params["prompt_group_id"] = params.pop("prompt_group_id", None) or None
    keywordsai_params["cache_enabled"] = params.pop("cache_enabled", None) or None
    keywordsai_params["cache_ttl"] = params.pop("cache_ttl", None) or None # Avoid unwanted 0
    keywordsai_params["time_to_first_token"] = params.pop("time_to_first_token", None) or None # Avoid unwanted 0
    keywordsai_params["ttft"] = params.pop("ttft", None) or None
    keywordsai_params["generation_time"] = params.pop("generation_time", None) or None # Avoid unwanted 0
    keywordsai_params["latency"] = params.pop("latency", None) or None
    keywordsai_params_pack = params.pop("keywordsai_params", None) or None
    if keywordsai_params_pack:
        try:
            keywordsai_params_pack = KeywordsAIParams.model_validate(
                keywordsai_params_pack
            ).model_dump()
            keywordsai_params.update(keywordsai_params_pack)
        except Exception as e:
            pass
    prompt_params = params.pop("prompt_params", {})
    llm_params = {}
    llm_params.update(prompt_params)
    llm_params.update(params)

    if remove_none:
        llm_params = {k: v for k, v in llm_params.items() if v is not None}
        keywordsai_params = {
            k: v for k, v in keywordsai_params.items() if v is not None
        }

    return llm_params, keywordsai_params

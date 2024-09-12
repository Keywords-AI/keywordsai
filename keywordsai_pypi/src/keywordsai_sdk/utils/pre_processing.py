from keywordsai_sdk.keywordsai_types._internal_types import KeywordsAIParams

def separate_params(params: dict, remove_none=False):
    """
    Separate the params into llm_params and keywordsai_params
    Returns:
    llm_params: dict
    keywordsai_params: dict
    """

    keywordsai_params = {}
    keywordsai_params["request_breakdown"] = params.pop("request_breakdown", False)
    keywordsai_params["ip_address"] = params.pop("ip_address", None)
    keywordsai_params["headers"] = params.pop("headers", None)
    keywordsai_params["cache_options"] = params.pop("cache_options", {})
    keywordsai_params["customer_credentials"] = params.pop("customer_credentials", {})
    keywordsai_params["disable_fallback"] = (
        params.pop("disable_fallback", False) or False
    )
    keywordsai_params["credential_override"] = params.pop("credential_override", {})
    keywordsai_params["load_balance_models"] = params.pop("load_balance_models", [])
    keywordsai_params["fallback_models"] = params.pop("fallback_models", [])
    keywordsai_params["for_eval"] = params.pop("for_eval", False) or False
    keywordsai_params["metadata"] = params.pop("metadata", {}) or {}
    keywordsai_params["disable_log"] = params.pop("disable_log", False) or False
    keywordsai_params["load_balance_group"] = params.pop("load_balance_group", None)
    keywordsai_params["trace_params"] = params.pop("trace_params", None)
    keywordsai_params["posthog_integration"] = params.pop("posthog_integration", None)
    keywordsai_params["customer_identifier"] = params.pop("customer_identifier", "")
    keywordsai_params["evaluation_identifier"] = params.pop("evaluation_identifier", "")
    keywordsai_params["model_name_map"] = params.pop("model_name_map", {})
    keywordsai_params["thread_identifier"] = params.pop("thread_identifier", "") or ""
    keywordsai_params["customer_email"] = params.pop("customer_email", "")
    keywordsai_params["delimiter"] = params.pop("delimiter", "---") or "---"
    keywordsai_params["fieldname"] = params.pop("fieldname", "") or ""
    keywordsai_params["prompt"] = params.pop("prompt", None) or None
    keywordsai_params["customer_params"] = params.pop("customer_params", {})
    keywordsai_params["prompt_group_id"] = params.pop("prompt_group_id", None)
    keywordsai_params["cache_enabled"] = params.pop("cache_enabled", False) or False
    keywordsai_params["cache_ttl"] = params.pop("cache_ttl", None)
    keywordsai_params["time_to_first_token"] = params.pop("time_to_first_token", None)
    keywordsai_params["ttft"] = params.pop("ttft", None)
    keywordsai_params["generation_time"] = params.pop("generation_time", None)
    keywordsai_params["latency"] = params.pop("latency", None)
    keywordsai_params_pack = params.pop("keywordsai_params", None)
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
        keywordsai_params = {k: v for k, v in keywordsai_params.items() if v is not None}

    return llm_params, keywordsai_params
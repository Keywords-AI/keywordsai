from respan_sdk.respan_types._internal_types import LiteLLMCompletionParams
from respan_sdk.respan_types.param_types import (
    RespanParams,
    RetryParams,
    EvaluationParams,
    BasicLLMParams,
    RespanAPIControlParams,
)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from respan_sdk.respan_types.log_types import RespanLogParams
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
    Separate the params into llm_params and respan_params
    If the params are falsely, they are removed from the dictionary (no params are valid with value 0)
    Returns:
    llm_params: dict
    respan_params: dict

    RULES:
        1. For cleanliness, all params that are default as False should end with "or None" as fallback so that they get removed
    """

    respan_params = {}
    respan_params["cache_enabled"] = params.pop("cache_enabled", None) or None
    respan_params["cache_options"] = params.pop("cache_options", None) or None
    respan_params["cache_ttl"] = (
        params.pop("cache_ttl", None) or None
    )  # Avoid unwanted 0
    respan_params["calling_model"] = params.get(
        "model", None
    )  # We want to make a copy of the model the user is calling, not remove
    respan_params["credential_override"] = (
        params.pop("credential_override", None) or None
    )
    respan_params["customer_credentials"] = (
        params.pop("customer_credentials", None) or None
    )
    respan_params["customer_email"] = params.pop("customer_email", "") or None
    respan_params["customer_identifier"] = (
        params.pop("customer_identifier", "") or None
    )
    respan_params["customer_params"] = params.pop("customer_params", None) or None
    respan_params["custom_identifier"] = (
        params.pop("custom_identifier", None) or None
    )
    respan_params["delimiter"] = params.pop("delimiter", "\n\n") or "---"
    respan_params["disable_fallback"] = params.pop("disable_fallback", None)
    respan_params["disable_log"] = params.pop("disable_log", None) or None
    if "evaluation_params" in params:
        assign_with_validation(
            retrieve_from=params,
            assign_to=respan_params,
            key="evaluation_params",
            type=EvaluationParams,
            raise_exception=raise_exception,
            mode="assign",
        )
    if "eval_params" in params:
        assign_with_validation(
            retrieve_from=params,
            assign_to=respan_params,
            key="eval_params",
            type=EvaluationParams,
            raise_exception=raise_exception,
            mode="assign",
        )
    respan_params["evaluation_identifier"] = (
        params.pop("evaluation_identifier", "") or None
    )
    respan_params["exclude_models"] = params.pop("exclude_models", None) or None
    respan_params["exclude_providers"] = (
        params.pop("exclude_providers", None) or None
    )
    respan_params["fallback_models"] = params.pop("fallback_models", None) or None
    respan_params["field_name"] = params.pop("field_name", "data: ") or ""
    respan_params["for_eval"] = params.pop("for_eval", None) or None
    respan_params["generation_time"] = (
        params.pop("generation_time", None) or None
    )  # Avoid unwanted 0
    respan_params["headers"] = params.pop("headers", None)
    respan_params["ip_address"] = params.pop("ip_address", None)
    assign_with_validation(
        retrieve_from=params,
        assign_to=respan_params,
        key="respan_api_controls",
        type=RespanAPIControlParams,
        raise_exception=raise_exception,
    )

    respan_params["latency"] = params.pop("latency", None) or None
    respan_params["load_balance_group"] = (
        params.pop("load_balance_group", None) or None
    )
    respan_params["load_balance_models"] = (
        params.pop("load_balance_models", None) or None
    )
    respan_params["metadata"] = params.pop("metadata", None) or None
    respan_params["model_name_map"] = params.pop("model_name_map", None) or None
    respan_params["posthog_integration"] = (
        params.pop("posthog_integration", None) or None
    )
    respan_params["prompt"] = params.pop("prompt", None) or None
    respan_params["prompt_group_id"] = params.pop("prompt_group_id", None) or None
    respan_params["prompt_version_number"] = (
        params.pop("prompt_version_number", None) or None
    )
    respan_params["request_breakdown"] = params.pop("request_breakdown", None)
    if "retry_params" in params:
        assign_with_validation(
            retrieve_from=params,
            assign_to=respan_params,
            key="retry_params",
            type=RetryParams,
            raise_exception=raise_exception,
            mode="override",
        )
    respan_params["thread_identifier"] = params.pop("thread_identifier", "") or None
    respan_params["time_to_first_token"] = (
        params.pop("time_to_first_token", None) or None
    )  # Avoid unwanted 0
    respan_params["trace_params"] = params.pop("trace_params", None) or None
    respan_params["ttft"] = params.pop("ttft", None) or None
    # Special case does not follow alphabetical order because it needs to override everything
    if "respan_params" in params:
        assign_with_validation(
            retrieve_from=params,
            assign_to=respan_params,
            key="respan_params",
            type=RespanParams,
            raise_exception=raise_exception,
            mode="override",
        )

    if remove_none:
        params = {k: v for k, v in params.items() if v is not None}
        respan_params = {
            k: v for k, v in respan_params.items() if v is not None
        }

    return params, respan_params


def validate_and_separate_params(
    params: dict,
) -> tuple[LiteLLMCompletionParams, RespanParams]:
    """
    Validate and separate the params into llm_params and respan_params using Pydantic models
    Returns:
    basic_llm: LiteLLMCompletionParams
    keywords_ai: RespanParams
    """

    basic_llm = LiteLLMCompletionParams.model_validate(params)
    keywords_ai = RespanParams.model_validate(params)

    return basic_llm, keywords_ai


def validate_and_separate_log_and_llm_params(
    params: dict,
) -> tuple[LiteLLMCompletionParams, "RespanLogParams"]:
    """
    Validate and separate the params into llm_params and public respan_log_params using Pydantic models.
    This function is intended for public-facing APIs and handles mapping of common LLM params to log params.

    Returns:
    basic_llm: LiteLLMCompletionParams
    keywords_ai_log: RespanLogParams
    """
    from respan_sdk.respan_types.log_types import RespanLogParams

    basic_llm = LiteLLMCompletionParams.model_validate(params)
    keywords_ai_log = RespanLogParams.model_validate(params)

    return basic_llm, keywords_ai_log

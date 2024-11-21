from typing import List, Literal, Optional
from typing_extensions import TypedDict
from pydantic import BaseModel, ConfigDict, field_validator, model_validator
from ._internal_types import (
    KeywordsAIParams,
    BasicLLMParams,
    KeywordsAIBaseModel,
    Customer,
)

"""
Conventions:

1. KeywordsAI as a prefix to class names
2. Params as a suffix to class names

Logging params types:
1. TEXT
2. EMBEDDING
3. AUDIO
4. GENERAL_FUNCTION
"""


class KeywordsAITextLogParams(KeywordsAIParams, BasicLLMParams):

    @field_validator("customer_params", mode="after")
    def validate_customer_params(cls, v: Customer):
        if v.customer_identifier is None:
            return None
        return v

    @model_validator(mode="before")
    def _preprocess_data(cls, data):
        data = KeywordsAIParams._preprocess_data(data)
        return data

    def serialize_for_logging(self) -> dict:
        # Define fields to include based on Django model columns
        # Using a set for O(1) lookup
        FIELDS_TO_INCLUDE = {
            "ip_address",
            "custom_identifier",
            "status",
            "unique_id",
            "prompt_tokens",
            "completion_tokens",
            "total_request_tokens",
            "cost",
            "amount_to_pay",
            "latency",
            "user_id",
            "organization_id",
            "model",
            "timestamp",
            "error_bit",
            "time_to_first_token",
            "metadata",
            "keywordsai_params",
            "stream",
            "stream_options",
            "thread_identifier",
            "status_code",
            "cached",
            "cache_bit",
            "full_request",
            "full_response",
            "tokens_per_second",
            "warnings",
            "recommendations",
            "error_message",
            "is_test",
            "environment",
            "temperature",
            "max_tokens",
            "logit_bias",
            "logprobs",
            "top_logprobs",
            "frequency_penalty",
            "presence_penalty",
            "stop",
            "n",
            "evaluation_cost",
            "evaluation_identifier",
            "for_eval",
            "customer_identifier",
            "customer_email",
            "used_custom_credential",
            "covered_by",
            "log_method",
            "log_type",
            "prompt_messages",
            "completion_message",
            "completion_messages",
            "tools",
            "tool_choice",
            "tool_calls",
            "has_tool_calls",
            "response_format",
            "parallel_tool_calls",
            "organization_key_id",
        }
        if self.disable_log:
            FIELDS_TO_INCLUDE.discard("full_request")
            FIELDS_TO_INCLUDE.discard("full_response")
            FIELDS_TO_INCLUDE.discard("tool_calls")
            FIELDS_TO_INCLUDE.discard("prompt_messages")
            FIELDS_TO_INCLUDE.discard("completion_messages")
            FIELDS_TO_INCLUDE.discard("completion_message")

        # Get all non-None values using model_dump
        data = self.model_dump(exclude_none=True)

        # Filter to only include fields that exist in Django model
        return {k: v for k, v in data.items() if k in FIELDS_TO_INCLUDE}

    model_config = ConfigDict(from_attributes=True)


class SimpleLogStats(KeywordsAIBaseModel):
    """
    Add default values to account for cases of error logs
    """

    total_request_tokens: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cost: float = 0
    organization_id: int
    user_id: int
    organization_key_id: str
    model: str | None = None
    metadata: dict | None = None
    used_custom_credential: bool = False

    def __init__(self, **data):
        for field_name in self.__annotations__:
            if field_name.endswith("_id"):
                related_model_name = field_name[:-3]  # Remove '_id' from the end
                self._assign_related_field(related_model_name, field_name, data)

        super().__init__(**data)

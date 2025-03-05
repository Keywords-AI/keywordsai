from keywordsai_sdk.keywordsai_types._internal_types import KeywordsAIParams
from enum import Enum

class KeywordsAISpanAttributes(Enum):
    # Span attributes
    KEYWORDSAI_SPAN_CUSTOM_ID = "keywordsai.span_params.custom_identifier"

    # Customer params
    KEYWORDSAI_CUSTOMER_PARAMS_ID = "keywordsai.customer_params.customer_identifier"
    KEYWORDSAI_CUSTOMER_PARAMS_EMAIL = "keywordsai.customer_params.email"
    KEYWORDSAI_CUSTOMER_PARAMS_NAME = "keywordsai.customer_params.name"
    
    # Evaluation params
    KEYWORDSAI_EVALUATION_PARAMS_ID = "keywordsai.evaluation_params.evaluation_identifier"

    # Threads
    KEYWORDSAI_THREADS_ID = "keywordsai.threads.thread_identifier"

    # Trace
    KEYWORDSAI_TRACE_GROUP_ID = "keywordsai.trace.trace_group_identifier"

    # Metadata
    KEYWORDSAI_METADATA = "keywordsai.metadata" # This is a pattern, it can be  any "keywordsai.metadata.key" where key is customizable

KEYWORDSAI_SPAN_ATTRIBUTES_MAP = {
    "customer_identifier": KeywordsAISpanAttributes.KEYWORDSAI_CUSTOMER_PARAMS_ID.value,
    "customer_email": KeywordsAISpanAttributes.KEYWORDSAI_CUSTOMER_PARAMS_EMAIL.value,
    "customer_name": KeywordsAISpanAttributes.KEYWORDSAI_CUSTOMER_PARAMS_NAME.value,
    "evaluation_identifier": KeywordsAISpanAttributes.KEYWORDSAI_EVALUATION_PARAMS_ID.value,
    "thread_identifier": KeywordsAISpanAttributes.KEYWORDSAI_THREADS_ID.value,
    "custom_identifier": KeywordsAISpanAttributes.KEYWORDSAI_SPAN_CUSTOM_ID.value,
    "trace_group_identifier": KeywordsAISpanAttributes.KEYWORDSAI_TRACE_GROUP_ID.value,
    "metadata": KeywordsAISpanAttributes.KEYWORDSAI_METADATA.value,
}
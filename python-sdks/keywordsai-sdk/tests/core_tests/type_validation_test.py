from keywordsai_sdk.keywordsai_types._internal_types import LiteLLMCompletionParams
from keywordsai_sdk.keywordsai_types.param_types import KeywordsAITextLogParams

NEW_SESSION_IDENTIFIER = 1234


class TypeValidationData:
    ttft: float
    generation_time: float
    organization: int
    hour_group: str
    minute_group: str
    timestamp: str
    log_type: str
    def __init__(self):
        self.ttft = 0.1
        self.generation_time = 0.2
        self.organization = 1
        self.hour_group = "2024-01-01T00:00:00"
        self.minute_group = "2024-01-01T00:00:00"
        self.timestamp = "2024-01-01T00:00:00"
        self.customer_identifier = "1234567890123456789123456789012345678901234567890123456789123456789012"
        self.reasoning = [{"reason": "This is a test"}]
        self.log_type = "text"
        self.trace_group_identifier = NEW_SESSION_IDENTIFIER
        self.thread_identifier = NEW_SESSION_IDENTIFIER


# Method 1: Convert to dict first
to_validate = TypeValidationData()
params = KeywordsAITextLogParams.model_validate(to_validate)
assert params.session_identifier == NEW_SESSION_IDENTIFIER


# Method 2: Use from_orm (deprecated but might work with older Pydantic)
# to_validate = TypeValidationData()
# params = KeywordsAITextLogParams.from_orm(to_validate)
# print(params)

data = {
    "messages": [
        {
            "role": "user",
            "content": "Hello, world!"
        }
    ]
}
validated_data = LiteLLMCompletionParams.model_validate(data).model_dump()

assert "thinking" not in validated_data

from keywordsai_sdk.keywordsai_types._internal_types import BasicTranscriptionParams, LiteLLMCompletionParams
from keywordsai_sdk.keywordsai_types.param_types import KeywordsAITextLogParams
from keywordsai_sdk.keywordsai_types.eval_types import EvalParams
from pydantic import ValidationError

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
        self.organization = 1
        self.hour_group = "2024-01-01T00:00:00"
        self.minute_group = "2024-01-01T00:00:00"
        self.timestamp = "2024-01-01T00:00:00"
        self.customer_identifier = "1234567890123456789123456789012345678901234567890123456789123456789012"
        self.reasoning = [{"reason": "This is a test"}]
        self.log_type = "text"
        self.trace_group_identifier = NEW_SESSION_IDENTIFIER
        self.thread_identifier = NEW_SESSION_IDENTIFIER
        self.response_format = "json"


# Method 1: Convert to dict first
to_validate = TypeValidationData()
params = KeywordsAITextLogParams.model_validate(to_validate)
assert params.session_identifier == NEW_SESSION_IDENTIFIER


# Method 2: Use from_orm (deprecated but might work with older Pydantic)
# to_validate = TypeValidationData()
# params = KeywordsAITextLogParams.from_orm(to_validate)
# print(params)


params = KeywordsAITextLogParams.model_validate(to_validate)
print(params)


# Test EvalParams with malformed message data
print("\n=== Testing EvalParams ===")

# Test 1: Should work with defaults
try:
    eval_params = EvalParams()
    print("✓ EvalParams with defaults works")
    print(f"Default completion_message: {eval_params.completion_message}")
except Exception as e:
    print(f"✗ EvalParams with defaults failed: {e}")

# Test 2: Should work with proper message data
try:
    eval_params = EvalParams(
        completion_message={"role": "user", "content": "test"},
        prompt_messages=[{"role": "system", "content": "system prompt"}]
    )
    print("✓ EvalParams with proper dict messages works")
except Exception as e:
    print(f"✗ EvalParams with proper dict messages failed: {e}")

# Test 3: Should break with malformed message data
try:
    eval_params = EvalParams(
        completion_message={"role": "invalid_role", "content": "test"},  # Invalid role
        prompt_messages=[{"role": "user"}]  # Missing content
    )
    print("✗ EvalParams with malformed messages should have failed but didn't!")
except ValidationError as e:
    print(f"✓ EvalParams properly caught validation error: {e}")
except Exception as e:
    print(f"? EvalParams failed with unexpected error: {e}")

# Test 4: Should break with completely wrong data types
try:
    eval_params = EvalParams(
        completion_message="this is not a message object",  # String instead of Message
        prompt_messages="this is also wrong"  # String instead of List[Message]
    )
    print("✗ EvalParams with wrong data types should have failed but didn't!")
except ValidationError as e:
    print(f"✓ EvalParams properly caught type validation error: {e}")
except Exception as e:
    print(f"? EvalParams failed with unexpected error: {e}")







KeywordsAITextLogParams(
    log_type="agent"
)

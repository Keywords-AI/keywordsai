from keywordsai_sdk.keywordsai_types.param_types import KeywordsAITextLogParams

class TestTypeValidation:
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
        # self.log_type= "some_random_shit"


# Method 1: Convert to dict first
to_validate = TestTypeValidation()
params = KeywordsAITextLogParams.model_validate(to_validate)
print(params)


# Method 2: Use from_orm (deprecated but might work with older Pydantic)
# to_validate = TestTypeValidation()
# params = KeywordsAITextLogParams.from_orm(to_validate)
# print(params)

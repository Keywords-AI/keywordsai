from keywordsai_sdk.keywordsai_types.param_types import KeywordsAITextLogParams

class TestTypeValidation:
    def __init__(self):
        self.ttft = 0.1
        self.generation_time = 0.2
        self.organization = 1
        self.hour_group = "2024-01-01T00:00:00"
        self.minute_group = "2024-01-01T00:00:00"
        self.timestamp = "2024-01-01T00:00:00"



to_validate= TestTypeValidation()
params = KeywordsAITextLogParams.model_validate(to_validate)
print(params)
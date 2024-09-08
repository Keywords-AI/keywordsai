from tests.test_env import *
from keywordsai_sdk.keywordsai_types.param_types import KeywordsAITextLogParams

from pydantic import BaseModel

kai_params = KeywordsAITextLogParams(
    model = test_model,
    prompt_messages=test_messages,
    completion_message=test_messages[1],
    latency=None
)



from typing import Optional
class TestModel(BaseModel):
    some_field: Optional[str] = None

model = TestModel(some_field=None)
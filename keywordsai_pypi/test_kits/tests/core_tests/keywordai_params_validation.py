from tests.test_env import *
from keywordsai.keywordsai_types.param_types import KeywordsAITextLogParams

kai_params = KeywordsAITextLogParams(
    model = test_model,
    prompt_messages=test_messages,
    completion_message=test_messages[1],
    latency=None
)


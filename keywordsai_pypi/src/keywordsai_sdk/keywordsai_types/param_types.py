from typing import List, Literal, Optional
from typing_extensions import TypedDict
from pydantic import BaseModel
from ._internal_types import (Message, FunctionTool, Trace
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
class KeywordsAIAPIControlParams(BaseModel):
    block: Optional[bool] = None

    def model_dump(self, *args, **kwargs):
        kwargs["exclude_none"] = True
        return super().model_dump(*args, **kwargs)
    
class KeywordsAILogParams(BaseModel):
    customer_identifier: Optional[str] = None
    evaluation_identifier: Optional[str] = None
    error_message: Optional[str] = None
    full_request: Optional[dict] = None
    metadata: Optional[dict] = None
    thread_identifier: Optional[str] = None
    trace_params: Optional[Trace] = None
    warnings: Optional[str] = None
    keywordsai_api_controls: Optional[KeywordsAIAPIControlParams] = None

class KeywordsAILogDict(TypedDict):
    customer_identifier: Optional[str] = None
    warnings: Optional[str] = None

class KeywordsAITextLogParams(KeywordsAILogParams):
    # Hard requirements
    completion_message: Message
    model: str = ""
    prompt_messages: List[Message]
    # Optional params
    completion_messages: List[Message] = None
    completion_tokens: Optional[int] = None
    completion_unit_price: Optional[float] = None
    cost: Optional[float] = None
    frequency_penalty: Optional[float] = None
    generation_time: Optional[float] = None # A mask over latency. TTFT + TPOT * tokens
    latency: Optional[float] = None # Required for tokens_per_second calculation
    max_tokens: Optional[int] = None
    n: Optional[int] = None
    top_p: Optional[float] = None
    presence_penalty: Optional[float] = None
    prompt_tokens: Optional[int] = None
    prompt_unit_price: Optional[float] = None
    response_format: Optional[dict] = None
    status_code: Optional[int] = None
    stop: Optional[List[str] | str] = None
    stream: Optional[bool] = None
    temperature: Optional[float] = None
    tools: Optional[List[FunctionTool]] = None
    time_to_first_token: Optional[float] = None # Required for tokens_per_second calculation
    ttft: Optional[float] = None # A mask over time_to_first_token

    def __init__(self, **data):
        data["time_to_first_token"] = data.get("time_to_first_token", data.get("ttft"))
        data["latency"] = data.get("latency", data.get("generation_time"))
        super().__init__(**data)
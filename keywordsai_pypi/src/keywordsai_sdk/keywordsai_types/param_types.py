from typing import List, Literal, Optional
from typing_extensions import TypedDict
from pydantic import BaseModel
from ._internal_types import (Message, FunctionTool
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
class KeywordsAILogParams(BaseModel):
    customer_identifier: Optional[str] = None
    warnings: Optional[List[str]] = None

class KeywordsAILogDict(TypedDict):
    customer_identifier: Optional[str] = None
    warnings: Optional[List[str]] = None
class KeywordsAITextLogParams(KeywordsAILogParams):
    completion_message: Message
    model: str = ""
    prompt_messages: List[Message]
    completion_messages: List[Message] = []
    completion_tokens: Optional[int] = None
    completion_unit_price: Optional[float] = None
    cost: Optional[float] = None
    error_message: Optional[str] = None
    full_request: Optional[dict] = None
    generation_time: Optional[float] = None # A mask over latency. TTFT + TPOT * tokens
    latency: Optional[float] = None
    metadata: Optional[dict] = None
    prompt_tokens: Optional[int] = None
    prompt_unit_price: Optional[float] = None
    response_format: Optional[dict] = None
    status_code: Optional[int] = None
    stream: Optional[bool] = None
    tools: Optional[List[FunctionTool]] = None
    time_to_first_token: Optional[float] = None
    ttft: Optional[float] = None # A mask over time_to_first_token
    tokens_per_second: Optional[float] = None

    def __init__(self, **data):
        data["time_to_first_token"] = data.get("time_to_first_token", data.get("ttft"))
        data["latency"] = data.get("latency", data.get("generation_time"))
        super().__init__(**data)
from typing import List, Literal, Optional
from typing_extensions import TypedDict
from pydantic import BaseModel, ConfigDict
from ._internal_types import KeywordsAIParams, BasicLLMParams
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

    model_config = ConfigDict(from_attributes=True)
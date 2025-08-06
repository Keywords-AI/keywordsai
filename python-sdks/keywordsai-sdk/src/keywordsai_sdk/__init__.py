# Main SDK exports
from .keywordsai_types import (
    # Public logging types - recommended for users
    KeywordsAILogParams,
    
    # Internal types
    KeywordsAIParams,
    KeywordsAIFullLogParams,
    KeywordsAITextLogParams,
    
    # Common parameter types
    EvaluationParams,
    RetryParams,
    Message,
    Usage,
)

from .utils.pre_processing import (
    validate_and_separate_params,
    validate_and_separate_log_and_llm_params,
)

__version__ = "1.0.0"

__all__ = [
    # Public types (recommended)
    "KeywordsAILogParams",
    "KeywordsAIFullLogParams",
    "KeywordsAITextLogParams",
    
    # Internal types (backward compatibility)
    "KeywordsAIParams",
    
    # Parameter types
    "EvaluationParams", 
    "RetryParams",
    "Message",
    "Usage",
    
    # Utility functions
    "validate_and_separate_params",
    "validate_and_separate_log_and_llm_params",
]

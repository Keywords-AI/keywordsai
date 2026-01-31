"""
Keywords AI Evaluator APIs

This module provides functionality for managing evaluators, including:
- Listing available evaluators
- Getting evaluator details
- Running evaluations
- Managing evaluation reports
"""

from respan.evaluators.api import (
    EvaluatorAPI,
    create_evaluator_client,
)
from respan.types.evaluator_types import (
    Evaluator,
    EvaluatorList,
)

# Export main classes and functions
__all__ = [
    "EvaluatorAPI",
    "create_evaluator_client",
    # Re-export types for convenience
    "Evaluator",
    "EvaluatorList",
]

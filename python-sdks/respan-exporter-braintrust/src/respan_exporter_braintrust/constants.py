"""Braintrust exporter constants.

Maps Braintrust span types to Respan log types.
"""

from respan_sdk.constants.llm_logging import (
    LOG_TYPE_CHAT,
    LOG_TYPE_CUSTOM,
    LOG_TYPE_FUNCTION,
    LOG_TYPE_GENERATION,
    LOG_TYPE_SCORE,
    LOG_TYPE_TASK,
    LOG_TYPE_TOOL,
    LOG_TYPE_WORKFLOW,
)

# Mapping of Braintrust span types to Respan log types
BRAINTRUST_SPAN_TYPE_TO_LOG_TYPE = {
    "llm": LOG_TYPE_GENERATION,
    "chat": LOG_TYPE_CHAT,
    "score": LOG_TYPE_SCORE,
    "function": LOG_TYPE_FUNCTION,
    "eval": LOG_TYPE_WORKFLOW,
    "task": LOG_TYPE_TASK,
    "tool": LOG_TYPE_TOOL,
    "automation": LOG_TYPE_WORKFLOW,
    "facet": LOG_TYPE_CUSTOM,
    "preprocessor": LOG_TYPE_CUSTOM,
}

from typing import Literal

MessageRoleType = Literal["user", "assistant", "system", "tool", "none", "developer"]

ResponseFormatType = Literal["text", "json", "json_object", "json_schema"]

ToolChoiceType = Literal["auto", "none", "required"]

ReasoningEffortType = Literal["low", "medium", "high"]

# Activity types
ACTIVITY_TYPE_PROMPT_CREATION: Literal["prompt_creation"] = "prompt_creation"
ACTIVITY_TYPE_COMMIT: Literal["commit"] = "commit"
ACTIVITY_TYPE_UPDATE: Literal["update"] = "update"
ACTIVITY_TYPE_DELETE: Literal["delete"] = "delete"

ActivityType = Literal["prompt_creation", "commit", "update", "delete"]

# Common model names (can be extended as needed)
DEFAULT_MODEL = "gpt-4o-mini"

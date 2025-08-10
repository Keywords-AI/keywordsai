export type MessageRoleType = "user" | "assistant" | "system" | "tool" | "none" | "developer";

export type ResponseFormatType = "text" | "json" | "json_object" | "json_schema";

export type ToolChoiceType = "auto" | "none" | "required";

export type ReasoningEffortType = "low" | "medium" | "high";

// Activity types
export const ACTIVITY_TYPE_PROMPT_CREATION = "prompt_creation" as const;
export const ACTIVITY_TYPE_COMMIT = "commit" as const;
export const ACTIVITY_TYPE_UPDATE = "update" as const;
export const ACTIVITY_TYPE_DELETE = "delete" as const;

export type ActivityType = "prompt_creation" | "commit" | "update" | "delete";

// Common model names (can be extended as needed)
export const DEFAULT_MODEL = "gpt-4o-mini";

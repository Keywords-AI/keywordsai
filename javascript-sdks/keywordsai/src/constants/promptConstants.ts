// Re-export all prompt constants from keywordsai-sdk
export type {
  // Message role types
  MessageRoleType,
  // Response format types
  ResponseFormatType,
  // Tool choice types
  ToolChoiceType,
  // Reasoning effort types
  ReasoningEffortType,
  // Activity types
  ActivityType,
} from "@keywordsai/keywordsai-sdk";

export {
  // Activity constants
  ACTIVITY_TYPE_PROMPT_CREATION,
  ACTIVITY_TYPE_COMMIT,
  ACTIVITY_TYPE_UPDATE,
  ACTIVITY_TYPE_DELETE,
  // Default model
  DEFAULT_MODEL,
} from "@keywordsai/keywordsai-sdk";

// Base paths
export const PROMPT_BASE_PATH = "/api/prompts";

// Specific endpoints
export const PROMPT_CREATION_PATH = `${PROMPT_BASE_PATH}`;
export const PROMPT_LIST_PATH = `${PROMPT_BASE_PATH}/list`;
export const PROMPT_GET_PATH = `${PROMPT_BASE_PATH}`;
export const PROMPT_UPDATE_PATH = `${PROMPT_BASE_PATH}`;
export const PROMPT_DELETE_PATH = `${PROMPT_BASE_PATH}`;

// Prompt version management endpoints
export const PROMPT_VERSION_CREATION_PATH = (promptId: string) => 
  `${PROMPT_BASE_PATH}/${promptId}/versions`;
export const PROMPT_VERSION_LIST_PATH = (promptId: string) => 
  `${PROMPT_BASE_PATH}/${promptId}/versions`;
export const PROMPT_VERSION_GET_PATH = (promptId: string) => 
  `${PROMPT_BASE_PATH}/${promptId}/versions`;
export const PROMPT_VERSION_UPDATE_PATH = (promptId: string) => 
  `${PROMPT_BASE_PATH}/${promptId}/versions`;

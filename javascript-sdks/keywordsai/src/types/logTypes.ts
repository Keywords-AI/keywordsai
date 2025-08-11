// Re-export log types from keywordsai-sdk
// Note: These types might have different names in the actual SDK
export type { KeywordsAIPayload as KeywordsAILogParams } from "@keywordsai/keywordsai-sdk";

// Import generic types
import type {
  PaginatedResponseType,
  KeywordsAIParams,
} from "@keywordsai/keywordsai-sdk";

// Type aliases for log responses
export type KeywordsAIFullLogParams = KeywordsAIParams;
export type LogList = PaginatedResponseType<KeywordsAIParams>;

// Re-export log types from respan-sdk
// Note: These types might have different names in the actual SDK
export type { RespanPayload as RespanLogParams } from "@respan/respan-sdk";

// Import generic types
import type {
  PaginatedResponseType,
  RespanParams,
} from "@respan/respan-sdk";

// Type aliases for log responses
export type RespanFullLogParams = RespanParams;
export type LogList = PaginatedResponseType<RespanParams>;

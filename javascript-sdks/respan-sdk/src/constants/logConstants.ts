// Mapping from Vercel AI SDK span types to Respan log types
// Define Respan log type enum
export enum RespanLogType {
  TEXT = "text",
  RESPONSE = "response",
  EMBEDDING = "embedding",
  TRANSCRIPTION = "transcription",
  SPEECH = "speech",
  WORKFLOW = "workflow",
  TASK = "task",
  TOOL = "tool",
  AGENT = "agent",
  HANDOFF = "handoff",
  GUARDRAIL = "guardrail",
  FUNCTION = "function",
  CUSTOM = "custom",
  GENERATION = "generation",
  UNKNOWN = "unknown",
}

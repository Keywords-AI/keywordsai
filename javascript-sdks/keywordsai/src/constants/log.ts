// Mapping from Vercel AI SDK span types to KeywordsAI log types
// Define KeywordsAI log type enum
export enum KeywordsLogType {
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
